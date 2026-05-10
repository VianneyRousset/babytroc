"""Pytest fixtures for the template chain and per-test DB clones."""

from __future__ import annotations

import os
import warnings
from typing import TYPE_CHECKING
from uuid import uuid4

import pytest
from broadcaster import Broadcast
from sqlalchemy import URL
from sqlalchemy.exc import SAWarning
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from babytroc.infrastructure.cache import init_cache_dependency
from babytroc.infrastructure.cache_client import NullCache
from babytroc.infrastructure.config import Config, S3Config
from babytroc.infrastructure.database import init_db_session_dependency
from babytroc.infrastructure.pubsub import init_broadcast_dependency
from tests.fixtures.database.infrastructure.admin import (
    create_database,
    drop_database,
)
from tests.fixtures.database.infrastructure.chain import (
    SeedContext,
    build_chain,
    teardown_chain,
)
from tests.fixtures.database.infrastructure.marker import get_template_name
from tests.fixtures.database.infrastructure.registry import (
    DEFAULT_TEMPLATE,
    TEMPLATES,
)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

warnings.simplefilter("error", SAWarning)


def _pg_base_url() -> URL:
    return URL.create(
        drivername="postgresql+asyncpg",
        username=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ["POSTGRES_PORT"]),
        database="postgres",
    )


def _seed_config() -> Config:
    """Config used during chain seed (notably for image upload to mocked S3)."""
    return Config.from_env(
        s3=S3Config(
            endpoint_url="http://localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            bucket="test-bucket",
            public_url="http://localhost:9000/test-bucket",
        ),
    )


@pytest.fixture(scope="session")
async def primary_databases(worker_id: str) -> AsyncGenerator[dict[str, URL]]:
    """Build the full template chain once per xdist worker. Yields name → URL."""
    base = _pg_base_url()
    # db_url is overridden per-template inside build_chain; pass any URL
    # here as a placeholder.
    ctx = SeedContext(config=_seed_config(), db_url=base)

    # Seed handlers (e.g. invalidate_cache_on_item_created,
    # loan_request_created) call get_cache() / get_broadcast() at chain
    # build time, before the app fixture initializes the real ones. Init
    # NullCache + an in-memory Broadcast so handlers don't crash; the
    # actual broadcast/cache backends are swapped in by the app fixture.
    init_cache_dependency(NullCache())
    init_broadcast_dependency(Broadcast("memory://"))

    urls = await build_chain(
        base_url=base,
        worker_id=worker_id,
        specs=TEMPLATES,
        ctx=ctx,
    )
    try:
        yield urls
    finally:
        await teardown_chain(urls)


@pytest.fixture(scope="session")
async def primary_database(primary_databases: dict[str, URL]) -> URL:
    """Compatibility shim — points at the current default template.

    Keeps `tests/fixtures/app.py::app_config` and the per-dir class-scoped
    `database` overrides in tests/{item,loan,chat_read}/conftest.py working
    until those callers migrate to markers + the new `database` fixture.
    """
    return primary_databases[DEFAULT_TEMPLATE]


@pytest.fixture
async def database(
    primary_databases: dict[str, URL],
    request: pytest.FixtureRequest,
    testrun_uid: str,
) -> AsyncGenerator[URL]:
    """Per-test DB cloned from the marker-selected template."""
    template_name = get_template_name(request)
    template_url = primary_databases[template_name]

    name = f"test-{uuid4()}-{testrun_uid}"
    url = template_url._replace(database=name)
    await create_database(url, template=template_url.database)
    try:
        yield url
    finally:
        await drop_database(url)


@pytest.fixture
async def database_sessionmaker(
    database: URL,
) -> AsyncGenerator[async_sessionmaker]:
    """Sessionmaker against the per-test DB; swaps it into the FastAPI app."""
    engine = create_async_engine(url=database, echo=False, poolclass=NullPool)
    maker = async_sessionmaker(bind=engine)
    init_db_session_dependency(maker)
    try:
        yield maker
    finally:
        await engine.dispose()
