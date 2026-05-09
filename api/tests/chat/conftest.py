"""Override fixtures to class-scoped for heavy chat tests."""

from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
from fastapi import FastAPI
from sqlalchemy import URL, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from babytroc.domains.image.schemas.read import ItemImageRead
from babytroc.domains.item.models.image import ItemImage
from babytroc.domains.region import services as region_services
from babytroc.domains.region.schemas.read import RegionRead
from babytroc.domains.user import services as user_services
from babytroc.domains.user.schemas.private import UserPrivateRead
from babytroc.infrastructure.cache_client import NullCache
from babytroc.infrastructure.database import init_db_session_dependency
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


@pytest.fixture(autouse=True, scope="class")
async def _swap_app_db(app: FastAPI, database_sessionmaker):
    """Class-scoped DB swap for heavy tests."""
    init_db_session_dependency(database_sessionmaker)
    yield


@pytest.fixture(autouse=True, scope="class")
async def _flush_redis(app: FastAPI):
    await app.state.redis.flushdb()
    yield
    await app.state.redis.flushdb()


@pytest.fixture(scope="class")
async def alice(database_sessionmaker: async_sessionmaker) -> UserPrivateRead:
    async with database_sessionmaker.begin() as session:
        return await user_services.get_user_by_email_private(
            session, "alice@babytroc.ch",
        )


@pytest.fixture(scope="class")
async def bob(database_sessionmaker: async_sessionmaker) -> UserPrivateRead:
    async with database_sessionmaker.begin() as session:
        return await user_services.get_user_by_email_private(
            session, "bob@babytroc.ch",
        )


@pytest.fixture(scope="class")
async def carol(database_sessionmaker: async_sessionmaker) -> UserPrivateRead:
    async with database_sessionmaker.begin() as session:
        return await user_services.get_user_by_email_private(
            session, "carol@babytroc.ch",
        )


@pytest.fixture(scope="class")
async def regions(
    database_sessionmaker: async_sessionmaker,
) -> list[RegionRead]:
    async with database_sessionmaker.begin() as session:
        return await region_services.list_regions(session, NullCache())


@pytest.fixture(scope="class")
async def alice_items_image(
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
) -> ItemImageRead:
    async with database_sessionmaker.begin() as session:
        row = (
            await session.execute(
                select(ItemImage)
                .where(ItemImage.owner_id == alice.id)
                .order_by(ItemImage.name)
                .limit(1)
            )
        ).scalar_one()
        return ItemImageRead.model_validate(row)


@pytest.fixture(scope="class")
async def bob_items_image(
    database_sessionmaker: async_sessionmaker,
    bob: UserPrivateRead,
) -> ItemImageRead:
    async with database_sessionmaker.begin() as session:
        row = (
            await session.execute(
                select(ItemImage)
                .where(ItemImage.owner_id == bob.id)
                .order_by(ItemImage.name)
                .limit(1)
            )
        ).scalar_one()
        return ItemImageRead.model_validate(row)
