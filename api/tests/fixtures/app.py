from collections.abc import AsyncGenerator

import pytest
import sqlalchemy
from asgi_lifespan import LifespanManager
from fastapi import FastAPI

from app.app import create_app
from app.config import Config, DatabaseConfig, PubsubConfig, RedisConfig


@pytest.fixture(scope="class")
async def app_config(
    database: sqlalchemy.URL,
) -> Config:
    """App config."""

    redis_config = RedisConfig.from_env(db=3)

    return Config.from_env(
        database=DatabaseConfig.from_env(
            url=database,
        ),
        pubsub=PubsubConfig(url=redis_config.url),
        redis=redis_config,
    )


@pytest.fixture(scope="class")
async def app(
    app_config: Config,
) -> AsyncGenerator[FastAPI]:
    app = create_app(app_config)
    async with LifespanManager(app):
        yield app


@pytest.fixture(autouse=True, scope="class")
async def flush_redis_cache(app: FastAPI):
    """Flush Redis test DB before each test class."""
    await app.state.redis.flushdb()
    yield
    await app.state.redis.flushdb()
