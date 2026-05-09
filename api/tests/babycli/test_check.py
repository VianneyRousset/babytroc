# tests/babycli/test_check.py
from unittest.mock import AsyncMock, MagicMock, patch

from babycli.check import check_email_config, check_postgres, check_redis, check_s3


async def test_check_postgres_success():
    mock_conn = AsyncMock()
    mock_conn.execute = AsyncMock(return_value=MagicMock(scalar=MagicMock(return_value="PostgreSQL 16.1")))

    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    with patch("babycli.check.async_db_session", return_value=mock_session):
        result = await check_postgres()
    assert result is True


async def test_check_postgres_failure():
    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(side_effect=Exception("connection refused"))
    mock_session.__aexit__ = AsyncMock(return_value=False)

    with patch("babycli.check.async_db_session", return_value=mock_session):
        result = await check_postgres()
    assert result is False


def test_check_email_config_valid():
    env = {
        "EMAIL_SERVER": "smtp.example.com",
        "EMAIL_PORT": "587",
        "EMAIL_USERNAME": "user",
        "EMAIL_PASSWORD": "pass",
        "EMAIL_FROM_EMAIL": "noreply@example.com",
        "EMAIL_FROM_NAME": "Babytroc",
    }
    with patch.dict("os.environ", env):
        result = check_email_config()
    assert result is True


def test_check_email_config_missing():
    with patch.dict("os.environ", {}, clear=True):
        result = check_email_config()
    assert result is False
