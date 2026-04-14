from collections.abc import AsyncGenerator

import pytest
import sqlalchemy
from asgi_lifespan import LifespanManager
from fastapi import FastAPI

from app.app import create_app
from app.config import Config, DatabaseConfig, PubsubConfig


@pytest.fixture(scope="class")
async def app_config(
    database: sqlalchemy.URL,
) -> Config:
    """App config."""

    return Config.from_env(
        database=DatabaseConfig.from_env(
            url=database,
        ),
        pubsub=PubsubConfig(
            url=sqlalchemy.URL.create(
                drivername="postgresql",
                username=database.username,
                password=database.password,
                host=database.host,
                port=database.port,
                database=database.database,
            ),
        ),
    )


@pytest.fixture(scope="class")
async def app(
    app_config: Config,
) -> AsyncGenerator[FastAPI]:
    app = await create_app(app_config)
    async with LifespanManager(app):
        yield app
