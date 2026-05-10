import httpx

from babytroc.infrastructure.cap import verify_cap_token
from babytroc.infrastructure.config import CapConfig

CONFIG = CapConfig(
    api_url="https://cap.example.com",
    site_key="site-1",
    secret_key="secret-1",
)

# Capture the real AsyncClient before any test monkeypatches httpx.AsyncClient,
# since patching `babytroc.infrastructure.cap.httpx.AsyncClient` mutates the
# shared httpx module and would otherwise cause _client_with to recurse.
_REAL_ASYNC_CLIENT = httpx.AsyncClient


def _client_with(transport: httpx.MockTransport) -> httpx.AsyncClient:
    return _REAL_ASYNC_CLIENT(transport=transport, timeout=5.0)


async def test_verify_cap_token_returns_true_on_success(monkeypatch):
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["body"] = request.read()
        return httpx.Response(200, json={"success": True})

    monkeypatch.setattr(
        "babytroc.infrastructure.cap.httpx.AsyncClient",
        lambda *a, **kw: _client_with(httpx.MockTransport(handler)),
    )
    assert await verify_cap_token(CONFIG, "token-abc") is True
    assert captured["url"] == "https://cap.example.com/site-1/siteverify"
    assert b"secret-1" in captured["body"]
    assert b"token-abc" in captured["body"]


async def test_verify_cap_token_returns_false_on_success_false(monkeypatch):
    def handler(request):
        return httpx.Response(200, json={"success": False})

    monkeypatch.setattr(
        "babytroc.infrastructure.cap.httpx.AsyncClient",
        lambda *a, **kw: _client_with(httpx.MockTransport(handler)),
    )
    assert await verify_cap_token(CONFIG, "bad-token") is False


async def test_verify_cap_token_returns_false_on_non_200(monkeypatch):
    def handler(request):
        return httpx.Response(500, json={"error": "boom"})

    monkeypatch.setattr(
        "babytroc.infrastructure.cap.httpx.AsyncClient",
        lambda *a, **kw: _client_with(httpx.MockTransport(handler)),
    )
    assert await verify_cap_token(CONFIG, "token") is False


async def test_verify_cap_token_returns_false_on_network_error(monkeypatch):
    def handler(request):
        msg = "server unreachable"
        raise httpx.ConnectError(msg)

    monkeypatch.setattr(
        "babytroc.infrastructure.cap.httpx.AsyncClient",
        lambda *a, **kw: _client_with(httpx.MockTransport(handler)),
    )
    assert await verify_cap_token(CONFIG, "token") is False


async def test_verify_cap_token_returns_false_on_invalid_json(monkeypatch):
    def handler(request):
        return httpx.Response(200, content=b"not json")

    monkeypatch.setattr(
        "babytroc.infrastructure.cap.httpx.AsyncClient",
        lambda *a, **kw: _client_with(httpx.MockTransport(handler)),
    )
    assert await verify_cap_token(CONFIG, "token") is False
