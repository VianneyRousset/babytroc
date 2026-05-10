from typing import TypedDict

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from babytroc.domains.user import services as user_services
from babytroc.domains.user.models import User
from babytroc.domains.user.schemas.private import UserPrivateRead


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


@pytest.fixture
async def many_users(
    database_sessionmaker: async_sessionmaker,
) -> list[UserPrivateRead]:
    """SELECT every user from the cloned DB.

    Backed by `tpl_many_users` (~256 random + the 3 baseline users).
    """
    async with database_sessionmaker.begin() as session:
        rows = (
            (await session.execute(select(User).order_by(User.id)))
            .scalars()
            .all()
        )
        return [UserPrivateRead.model_validate(r) for r in rows]
