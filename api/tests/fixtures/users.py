import random
from string import ascii_letters
from typing import TypedDict

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from babytroc.domains.user import services as user_services
from babytroc.domains.user.schemas.create import UserCreate
from babytroc.domains.user.schemas.private import UserPrivateRead
from babytroc.shared.hash import HashedStr


class UserData(TypedDict):
    name: str
    email: str
    password: str


@pytest.fixture(scope="session")
def alice_user_data() -> UserData:
    """Alice user data."""

    return {
        "name": "alice",
        "email": "alice@babytroc.ch",
        "password": "password-Alice-42",
    }


@pytest.fixture(scope="session")
def bob_user_data() -> UserData:
    """Bob user data."""

    return {
        "name": "bob",
        "email": "bob@babytroc.ch",
        "password": "password-Bob-42",
    }


@pytest.fixture(scope="session")
def carol_user_data() -> UserData:
    """Carol user data."""

    return {
        "name": "carol",
        "email": "carol@babytroc.ch",
        "password": "password-Carol-42",
    }


@pytest.fixture
async def alice(
    database_sessionmaker: async_sessionmaker,
) -> UserPrivateRead:
    """Fetches the pre-seeded Alice user."""

    async with database_sessionmaker.begin() as session:
        return await user_services.get_user_by_email_private(session, "alice@babytroc.ch")


@pytest.fixture
async def bob(
    database_sessionmaker: async_sessionmaker,
) -> UserPrivateRead:
    """Fetches the pre-seeded Bob user."""

    async with database_sessionmaker.begin() as session:
        return await user_services.get_user_by_email_private(session, "bob@babytroc.ch")


@pytest.fixture
async def carol(
    database_sessionmaker: async_sessionmaker,
) -> UserPrivateRead:
    """Fetches the pre-seeded Carol user."""

    async with database_sessionmaker.begin() as session:
        return await user_services.get_user_by_email_private(session, "carol@babytroc.ch")


def random_str(length: int) -> str:
    return "".join(random.choices(ascii_letters, k=length))


@pytest.fixture(scope="class")
async def many_users(
    database_sessionmaker: async_sessionmaker,
) -> list[UserPrivateRead]:
    """Many users."""

    n = 256
    random.seed(0x538D)

    password_hash = HashedStr("xyzXYZ123")

    user_creates = [
        UserCreate(
            name=random_str(8),
            email=f"{random_str(8)}@{random_str(8)}.com",
            password=password_hash,
        )
        for _ in range(n)
    ]

    async with database_sessionmaker.begin() as session:
        return await user_services.create_many_users_without_validation(
            session,
            user_creates=user_creates,
            validated=True,
        )
