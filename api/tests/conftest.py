import os
import random
import string
import warnings
from collections.abc import Generator
from pathlib import Path

import pytest
import sqlalchemy
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy_utils import create_database, drop_database

from alembic import command
from alembic.config import Config as AlembicConfig
from app.app import create_app
from app.config import Config, ImgPushConfig
from app.schemas.user.create import UserCreate
from app.services.user import create_user


def random_string(length: int):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(length))


@pytest.fixture
def database() -> Generator[sqlalchemy.URL]:
    database = random_string(4)

    postgres_url = sqlalchemy.URL.create(
        "postgresql+psycopg2",
        username=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ["POSTGRES_PORT"]),
        database=database,
    )

    create_database(postgres_url)

    app_root = Path(__file__).parent.parent
    alembic_cfg = AlembicConfig(app_root / "alembic.ini")
    alembic_cfg.set_main_option("script_location", str(app_root / "alembic"))
    alembic_cfg.set_main_option(
        "sqlalchemy.url", postgres_url.render_as_string(hide_password=False)
    )
    command.upgrade(alembic_cfg, "head")

    yield postgres_url

    drop_database(postgres_url)


@pytest.fixture
def database_user(database: sqlalchemy.URL) -> int:
    # make sqlalchemy warnings as errors
    warnings.simplefilter("error", sqlalchemy.exc.SAWarning)

    engine = create_engine(database)
    with Session(engine) as session, session.begin():
        user = create_user(
            session,
            UserCreate(
                name="test",
                email="test@example.com",
                password="test",
            ),
        )

        return user.id


@pytest.fixture
def client(database: sqlalchemy.URL) -> TestClient:
    config = Config(
        postgres_url=database,
        imgpush=ImgPushConfig.from_env(),
    )

    return TestClient(create_app(config))
