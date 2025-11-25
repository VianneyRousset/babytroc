import os
import warnings
from collections.abc import AsyncGenerator
from pathlib import Path
from uuid import uuid4

import pytest
from alembic.config import Config as AlembicConfig
from sqlalchemy import URL, text
from sqlalchemy.exc import SAWarning
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from alembic import command

# make sqlalchemy warnings as errors
warnings.simplefilter("error", SAWarning)


@pytest.fixture(scope="session")
async def primary_database() -> AsyncGenerator[URL]:
    name = f"test-primary_database-{uuid4()}"

    # create URL
    url = URL.create(
        drivername="postgresql+asyncpg",
        username=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ["POSTGRES_PORT"]),
        database=name,
    )

    # create database
    await create_database(url)

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
    await drop_database(url)


@pytest.fixture(scope="class")
async def database(
    primary_database: URL,
    testrun_uid: str,
) -> AsyncGenerator[URL]:
    """Create a temporary database with alembic migrations applied."""

    name = f"test-{uuid4()}-{testrun_uid}"

    # create URL
    url = URL.create(
        drivername=primary_database.drivername,
        username=primary_database.username,
        password=primary_database.password,
        host=primary_database.host,
        port=primary_database.port,
        database=name,
    )

    # create database
    await create_database(url, template=primary_database.database)

    # yield database url
    yield url

    return

    # destroy database
    await drop_database(url)


@pytest.fixture(scope="class")
async def database_sessionmaker(
    database: URL,
) -> AsyncGenerator[async_sessionmaker]:
    engine = create_async_engine(
        url=database,
        echo=False,
    )

    yield async_sessionmaker(
        bind=engine,
    )

    await engine.dispose()


async def create_database(
    url: URL,
    *,
    encoding="utf8",
    template=None,
) -> None:
    database = url.database
    url = url._replace(database="postgres")

    engine = create_async_engine(url)

    # postgres default database template
    if template is None:
        template = "template1"

    try:
        async with engine.begin() as conn:
            stmt = text(
                f'CREATE DATABASE "{database}" '
                f"ENCODING '{encoding}' "
                f'TEMPLATE "{template}"'
            )
            await conn.execute(stmt)

    finally:
        await engine.dispose()


async def drop_database(url: URL) -> None:
    database = url.database
    url = url._replace(database="postgres")

    engine = create_async_engine(url)

    try:
        async with engine.begin() as conn:
            stmt = text(f'DROP DATABASE "{database}"')
            await conn.execute(stmt)

    finally:
        await engine.dispose()

    await engine.dispose()
