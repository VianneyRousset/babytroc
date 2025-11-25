import pytest
import sqlalchemy

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
