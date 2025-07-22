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
def alice(
    database: sqlalchemy.URL,
    alice_user_data: UserData,
) -> UserPrivateRead:
    """Ensures Alice exists."""

    engine = create_engine(database)
    with Session(engine) as session, session.begin():
        return services.user.create_user_without_validation(
            session,
            UserCreate(**alice_user_data),
            validated=True,
        )


@pytest.fixture(scope="class")
def bob(
    database: sqlalchemy.URL,
    bob_user_data: UserData,
) -> UserPrivateRead:
    """Ensures Bob exists."""

    engine = create_engine(database)
    with Session(engine) as session, session.begin():
        return services.user.create_user_without_validation(
            session,
            UserCreate(**bob_user_data),
            validated=True,
        )


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

    engine = create_engine(database)
    with Session(engine) as session, session.begin():
        return [
            services.user.create_user_without_validation(
                session,
                UserCreate(
                    name=random_str(8),
                    email=f"{random_str(8)}@{random_str(8)}.com",
                    password="xyzXYZ123",  # noqa: S106
                ),
                validated=True,
            )
            for _ in range(n)
        ]
