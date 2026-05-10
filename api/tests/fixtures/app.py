from collections.abc import AsyncGenerator
from datetime import timedelta

import pytest
import sqlalchemy
from asgi_lifespan import LifespanManager
from fastapi import FastAPI

from babytroc.app import create_app
from babytroc.infrastructure.config import (
    CapConfig,
    Config,
    ContactConfig,
    DatabaseConfig,
    PubsubConfig,
    RedisConfig,
    S3Config,
)


@pytest.fixture(scope="session")
async def app_config(
    primary_database: sqlalchemy.URL,
    worker_id: str,
) -> Config:
    if worker_id == "master":
        redis_db = 3
    else:
        redis_db = 3 + int(worker_id.replace("gw", ""))

    redis_config = RedisConfig.from_env(db=redis_db)

    return Config.from_env(
        database=DatabaseConfig.from_env(url=primary_database),
        pubsub=PubsubConfig(url=redis_config.url),
        redis=redis_config,
        s3=S3Config(
            endpoint_url="http://localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            bucket="test-bucket",
            public_url="http://localhost:9000/test-bucket",
        ),
        contact=ContactConfig(
            email="test-contact@babytroc.ch",
            rate_limit_anon=5,
            rate_limit_auth=10,
            rate_limit_window=timedelta(seconds=3600),
        ),
        cap=CapConfig(
            api_url="https://cap.test.invalid",
            site_key="test-site-key",
            secret_key="test-secret-key",
        ),
    )


@pytest.fixture(scope="session")
async def app(
    app_config: Config,
    worker_id: str,
) -> AsyncGenerator[FastAPI]:
    prefix = f"worker-{worker_id}:"
    app = create_app(app_config, pubsub_channel_prefix=prefix)
    async with LifespanManager(app):
        yield app


@pytest.fixture(autouse=True)
async def _flush_redis(app: FastAPI):
    await app.state.redis.flushdb()
    yield
    await app.state.redis.flushdb()
