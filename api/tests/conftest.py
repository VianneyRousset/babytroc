import os
from pathlib import Path

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Connection, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

import alembic.command
import alembic.config
from app.app import create_app

from .seed import apply_seed


async def create_database(postgres_url: str, db_name: str) -> AsyncEngine:
    """Create a new initialized database with the given db_name and return engine."""

    # create engine
    engine = create_async_engine(
        url=f"{postgres_url}",
        echo=False,
    )

    # create new database
    async with engine.connect() as conn:
        conn = await conn.execution_options(isolation_level="AUTOCOMMIT")
        await conn.execute(text(f'CREATE DATABASE "{db_name}"'))
        await conn.commit()

    # create engine to the new database
    engine = create_async_engine(
        url=f"{postgres_url}/{db_name}",
        echo=False,
    )

    # run migrations
    await run_migrations(
        engine=engine,
    )

    return engine


def create_sessionmaker(db_engine: AsyncEngine) -> async_sessionmaker:
    # create session maker to the new database
    return async_sessionmaker(
        bind=db_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )


async def run_migrations(
    engine: AsyncEngine,
    config_path: Path | str = "alembic.ini",
    revision: str = "head",
):
    def run_sync_migrations(connection: Connection):
        config = alembic.config.Config("alembic.ini")
        config.attributes["connection"] = connection

        alembic.command.upgrade(
            config=config,
            revision="head",
        )

    async with engine.begin() as connection:
        await connection.run_sync(
            run_sync_migrations,
        )


@pytest.fixture(scope="class")
async def postrgres_user() -> str:
    return os.environ["POSTGRES_USER"]


@pytest.fixture(scope="class")
async def postrgres_password() -> str:
    return os.environ["POSTGRES_PASSWORD"]


@pytest.fixture(scope="class")
async def postgres_port() -> str:
    return os.environ["POSTGRES_PORT"]


@pytest.fixture(scope="class")
async def postgres_url(
    postrgres_user: str, postrgres_password: str, postgres_port: str
) -> str:
    return (
        f"postgresql+asyncpg://{postrgres_user}:{postrgres_password}@db:{postgres_port}"
    )


@pytest.fixture(scope="class")
async def db_name(request: pytest.FixtureRequest) -> str:
    return f"test-{request.cls.__name__}-{id(request.cls)}"


@pytest.fixture(scope="class")
async def db_engine(postgres_url: str, db_name: str) -> AsyncEngine:
    engine = await create_database(
        postgres_url=postgres_url,
        db_name=db_name,
    )
    return engine


@pytest.fixture(scope="class")
async def sessionmaker(db_engine: AsyncEngine) -> async_sessionmaker:
    return create_sessionmaker(db_engine)


@pytest.fixture
async def db(sessionmaker: async_sessionmaker) -> AsyncSession:
    async with sessionmaker() as session:
        yield session


@pytest.fixture(scope="class")
async def client(db_engine: AsyncEngine) -> AsyncClient:
    app = create_app(db_engine.sync_engine.url)

    async with LifespanManager(app):
        transport = ASGITransport(app)
        async with AsyncClient(
            transport=transport, base_url="http://localhost:8080"
        ) as ac:
            yield ac


@pytest.fixture(scope="class")
async def _seed_db(sessionmaker: async_sessionmaker) -> None:
    async with sessionmaker() as session:
        await apply_seed(session)
