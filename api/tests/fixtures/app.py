import pytest
import sqlalchemy

from app.config import Config, DatabaseConfig


@pytest.fixture(scope="class")
def app_config(
    database: sqlalchemy.URL,
) -> Config:
    """App config."""

    return Config.from_env(
        database=DatabaseConfig.from_env(
            url=database,
        ),
    )
