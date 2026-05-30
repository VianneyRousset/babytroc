# tests/babycli/test_check.py
from unittest.mock import AsyncMock, MagicMock, patch

import httpx

from babycli.check import check_cap, check_postgres

# Capture the real AsyncClient before any test monkeypatches httpx.AsyncClient,
# since patching `babycli.check.httpx.AsyncClient` mutates the shared httpx
# module and would otherwise cause the lambda factory to recurse.
_REAL_ASYNC_CLIENT = httpx.AsyncClient


def _client_with(transport: httpx.MockTransport) -> httpx.AsyncClient:
    return _REAL_ASYNC_CLIENT(transport=transport, timeout=5.0)


async def test_check_postgres_success():
    mock_conn = AsyncMock()
    mock_conn.execute = AsyncMock(
        return_value=MagicMock(scalar=MagicMock(return_value="PostgreSQL 16.1"))
    )

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


async def test_check_cap_success(monkeypatch):
    env = {
        "CAP_API_URL": "https://cap.example.com",
        "CAP_SITE_KEY": "site",
        "CAP_SECRET_KEY": "secret",
    }

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200)

    monkeypatch.setattr(
        "babycli.check.httpx.AsyncClient",
        lambda *a, **kw: _client_with(httpx.MockTransport(handler)),
    )
    with patch.dict("os.environ", env, clear=True):
        result = await check_cap()
    assert result is True


async def test_check_cap_failure_on_network_error(monkeypatch):
    env = {
        "CAP_API_URL": "https://cap.example.com",
        "CAP_SITE_KEY": "site",
        "CAP_SECRET_KEY": "secret",
    }

    def handler(request):
        msg = "unreachable"
        raise httpx.ConnectError(msg)

    monkeypatch.setattr(
        "babycli.check.httpx.AsyncClient",
        lambda *a, **kw: _client_with(httpx.MockTransport(handler)),
    )
    with patch.dict("os.environ", env, clear=True):
        result = await check_cap()
    assert result is False


async def test_check_cap_accepts_non_200(monkeypatch):
    """A 404 still proves the cap server is reachable."""
    env = {
        "CAP_API_URL": "https://cap.example.com",
        "CAP_SITE_KEY": "site",
        "CAP_SECRET_KEY": "secret",
    }

    def handler(request):
        return httpx.Response(404)

    monkeypatch.setattr(
        "babycli.check.httpx.AsyncClient",
        lambda *a, **kw: _client_with(httpx.MockTransport(handler)),
    )
    with patch.dict("os.environ", env, clear=True):
        result = await check_cap()
    assert result is True
