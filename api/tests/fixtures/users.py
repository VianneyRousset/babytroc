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
        "email": "alice@ekindbaby.ch",
        "password": "password-alice",
    }


@pytest.fixture(scope="class")
def bob_user_data() -> UserData:
    """Bob user data."""

    return {
        "name": "bob",
        "email": "bob@ekindbaby.ch",
        "password": "password-bob",
    }


@pytest.fixture(scope="class")
def alice(
    database: sqlalchemy.URL,
    alice_user_data: UserData,
) -> UserPrivateRead:
    """Ensures Alice exists."""

    engine = create_engine(database)
    with Session(engine) as session, session.begin():
        return UserPrivateRead.model_validate(
            services.user.create_user(session, UserCreate(**alice_user_data))
        )


@pytest.fixture(scope="class")
def bob(
    database: sqlalchemy.URL,
    bob_user_data: UserData,
) -> UserPrivateRead:
    """Ensures Bob exists."""

    engine = create_engine(database)
    with Session(engine) as session, session.begin():
        return UserPrivateRead.model_validate(
            services.user.create_user(session, UserCreate(**bob_user_data))
        )
