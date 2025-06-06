import os
import random
import string
import warnings
from collections.abc import Generator
from pathlib import Path

import pytest
import sqlalchemy
from sqlalchemy_utils import create_database, drop_database

from alembic import command
from alembic.config import Config as AlembicConfig

# make sqlalchemy warnings as errors
warnings.simplefilter("error", sqlalchemy.exc.SAWarning)


def random_string(length: int):
    """Generate a random string."""

    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(length))


@pytest.fixture(scope="session")
def primary_database() -> Generator[sqlalchemy.URL]:
    name = "test_primary_database-" + random_string(8)

    # create URL
    url = sqlalchemy.URL.create(
        drivername="postgresql+psycopg2",
        username=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ["POSTGRES_PORT"]),
        database=name,
    )

    # create database
    create_database(url)

    # apply alembic migrations
    app_root = Path(__file__).parent.parent.parent
    alembic_cfg = AlembicConfig(app_root / "alembic.ini")
    alembic_cfg.set_main_option("script_location", str(app_root / "alembic"))
    alembic_cfg.set_main_option(
        "sqlalchemy.url", url.render_as_string(hide_password=False)
    )
    command.upgrade(alembic_cfg, "head")

    # yield database url
    yield url

    # destroy database
    drop_database(url)


@pytest.fixture(scope="class")
def database(primary_database: sqlalchemy.URL) -> Generator[sqlalchemy.URL]:
    """Create a temporary database with alembic migrations applied."""

    # create URL
    url = sqlalchemy.URL.create(
        drivername=primary_database.drivername,
        username=primary_database.username,
        password=primary_database.password,
        host=primary_database.host,
        port=primary_database.port,
        database=random_string(8),
    )

    # create database
    create_database(url, template=primary_database.database)

    # yield database url
    yield url

    # destroy database
    drop_database(url)
