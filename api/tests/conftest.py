from collections.abc import Generator
from pathlib import Path
import os
import random
import string

from alembic.config import Config as AlembicConfig
from alembic import command
from fastapi.testclient import TestClient
from pytest import fixture
from sqlalchemy import create_engine, URL as sqlURL
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy_utils import create_database, drop_database

from app.app import create_app
from app.config import Config
from app.schemas.user.create import UserCreate
from app.services.user import create_user


def random_string(length: int):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(length))


@fixture
def database() -> Generator[sqlURL]:
    database = random_string(4)

    postgres_url = sqlURL.create(
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


@fixture
def database_user(database: sqlURL) -> int:
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


@fixture
def client(database: sqlURL) -> TestClient:
    config = Config(
        postgres_url=database,
        imgpush=Config.ImgPush.from_env(),
    )

    return TestClient(create_app(config))
