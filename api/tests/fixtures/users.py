import random
from string import ascii_letters
from typing import TypedDict

import pytest
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import services
from app.schemas.user.create import UserCreate
from app.schemas.user.private import UserPrivateRead
from app.utils.hash import HashedStr


class UserData(TypedDict):
    name: str
    email: str
    password: str


@pytest.fixture(scope="class")
def alice_user_data() -> UserData:
    """Alice user data."""

    return {
        "name": "alice",
        "email": "alice@babytroc.ch",
        "password": "password-Alice-42",
    }


@pytest.fixture(scope="class")
def bob_user_data() -> UserData:
    """Bob user data."""

    return {
        "name": "bob",
        "email": "bob@babytroc.ch",
        "password": "password-Bob-42",
    }


@pytest.fixture(scope="class")
def carol_user_data() -> UserData:
    """Carol user data."""

    return {
        "name": "carol",
        "email": "carol@babytroc.ch",
        "password": "password-Carol-42",
    }


@pytest.fixture(scope="class")
def alice(
    database: sqlalchemy.URL,
    alice_user_data: UserData,
) -> UserPrivateRead:
    """Ensures Alice exists."""

    engine = create_engine(database)

    with Session(engine) as session, session.begin():
        return services.user.create_many_users_without_validation(
            session,
            [UserCreate(**alice_user_data)],
            validated=True,
        )[0]


@pytest.fixture(scope="class")
def bob(
    database: sqlalchemy.URL,
    bob_user_data: UserData,
) -> UserPrivateRead:
    """Ensures Bob exists."""

    engine = create_engine(database)
    with Session(engine) as session, session.begin():
        return services.user.create_many_users_without_validation(
            session,
            [UserCreate(**bob_user_data)],
            validated=True,
        )[0]


@pytest.fixture(scope="class")
def carol(
    database: sqlalchemy.URL,
    carol_user_data: UserData,
) -> UserPrivateRead:
    """Ensures Carol exists."""

    engine = create_engine(database)
    with Session(engine) as session, session.begin():
        return services.user.create_many_users_without_validation(
            session,
            [UserCreate(**carol_user_data)],
            validated=True,
        )[0]


def random_str(length: int) -> str:
    return "".join(random.choices(ascii_letters, k=length))


@pytest.fixture(scope="class")
def many_users(
    database: sqlalchemy.URL,
    bob_user_data: UserData,
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

    engine = create_engine(database)
    with Session(engine) as session, session.begin():
        return services.user.create_many_users_without_validation(
            session,
            user_creates=user_creates,
            validated=True,
        )
