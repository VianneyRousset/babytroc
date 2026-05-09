"""Override database to class-scoped for heavy pagination tests."""

from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from tests.fixtures.database import create_database, drop_database


@pytest.fixture(scope="class")
async def database(
    primary_database: URL,
    testrun_uid: str,
) -> AsyncGenerator[URL]:
    name = f"test-{uuid4()}-{testrun_uid}"
    url = URL.create(
        drivername=primary_database.drivername,
        username=primary_database.username,
        password=primary_database.password,
        host=primary_database.host,
        port=primary_database.port,
        database=name,
    )
    await create_database(url, template=primary_database.database)
    yield url
    await drop_database(url)


@pytest.fixture(scope="class")
async def database_sessionmaker(
    database: URL,
) -> AsyncGenerator[async_sessionmaker]:
    engine = create_async_engine(
        url=database, echo=False, poolclass=NullPool,
    )
    yield async_sessionmaker(bind=engine)
    await engine.dispose()
