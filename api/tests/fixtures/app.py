from collections.abc import AsyncGenerator

import pytest
import sqlalchemy
from asgi_lifespan import LifespanManager
from fastapi import FastAPI

from babytroc.app import create_app
from babytroc.infrastructure.config import (
    Config,
    DatabaseConfig,
    PubsubConfig,
    RedisConfig,
    S3Config,
)


@pytest.fixture(scope="class")
async def app_config(
    database: sqlalchemy.URL,
    worker_id: str,
) -> Config:
    """App config."""

    # Each xdist worker gets its own Redis DB to avoid cross-worker flushdb races.
    # worker_id is "master" (no xdist) or "gw0", "gw1", etc.
    if worker_id == "master":
        redis_db = 3
    else:
        redis_db = 3 + int(worker_id.replace("gw", ""))

    redis_config = RedisConfig.from_env(db=redis_db)

    return Config.from_env(
        database=DatabaseConfig.from_env(
            url=database,
        ),
        pubsub=PubsubConfig(url=redis_config.url),
        redis=redis_config,
        s3=S3Config(
            endpoint_url="http://localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            bucket="test-bucket",
            public_url="http://localhost:9000/test-bucket",
        ),
    )


@pytest.fixture(scope="class")
async def app(
    app_config: Config,
    database: sqlalchemy.URL,
) -> AsyncGenerator[FastAPI]:
    # Use the unique database name as pub/sub channel prefix to avoid
    # cross-talk between xdist workers sharing the same Redis instance.
    prefix = f"{database.database}:" if database.database else ""
    app = create_app(app_config, pubsub_channel_prefix=prefix)
    async with LifespanManager(app):
        yield app


@pytest.fixture(autouse=True, scope="class")
async def flush_redis_cache(app: FastAPI):
    """Flush Redis test DB before each test class."""
    await app.state.redis.flushdb()
    yield
    await app.state.redis.flushdb()
