from collections.abc import AsyncGenerator, Callable
from datetime import timedelta
from typing import Any

import pytest
from fastapi import FastAPI

from babytroc.infrastructure import cap as cap_module
from babytroc.shared.rate_limit import RateLimiter


@pytest.fixture
def cap_verify_result() -> bool:
    """Override in tests via `@pytest.mark.parametrize` or direct fixture override
    to make the stubbed cap verifier return False."""
    return True


@pytest.fixture
def cap_verify_raises() -> bool:
    """Override to make the stubbed cap verifier raise an httpx error path."""
    return False


@pytest.fixture(autouse=True)
def stub_cap_verify(
    monkeypatch: pytest.MonkeyPatch,
    cap_verify_result: bool,
    cap_verify_raises: bool,
):
    """Replace `verify_cap_token` so tests don't reach a real cap server.

    The contact router imports `verify_cap_token` from `babytroc.infrastructure.cap`,
    so we patch the symbol *on the module the router imported it from*. Because
    `babytroc.routers.v1.utils.contact` does `from babytroc.infrastructure.cap import
    verify_cap_token`, we patch both locations.
    """

    async def _fake(_config, _token):
        if cap_verify_raises:
            import httpx

            msg = "boom"
            raise httpx.ConnectError(msg)
        return cap_verify_result

    monkeypatch.setattr(cap_module, "verify_cap_token", _fake)
    # The router binds the symbol at import time; patch its bound reference too
    # if the import has already happened.
    try:
        from babytroc.routers.v1.utils import contact as contact_router_module

        monkeypatch.setattr(contact_router_module, "verify_cap_token", _fake)
    except ImportError:
        pass


@pytest.fixture
def tight_rate_limit_factory(app: FastAPI) -> Callable[..., Any]:
    """Return a function that overrides the contact rate limiter with tight values
    (short window) so rate-limit tests run fast.

    Usage in a test:
        tight_rate_limit_factory(anon_limit=2, auth_limit=3, window_seconds=60)
    """

    def _set(*, anon_limit: int, auth_limit: int, window_seconds: int) -> None:
        from babytroc.routers.v1.utils.contact import (  # type: ignore[import-untyped]
            rate_limit_contact as original,
        )

        new = RateLimiter(
            key_prefix="contact-test",
            anon_limit=anon_limit,
            auth_limit=auth_limit,
            window=timedelta(seconds=window_seconds),
        )
        app.dependency_overrides[original] = new

    return _set


@pytest.fixture(autouse=True)
async def _clear_contact_overrides(app: FastAPI) -> AsyncGenerator[None]:
    yield
    # Remove any overrides set by tight_rate_limit_factory after each test.
    try:
        from babytroc.routers.v1.utils.contact import rate_limit_contact

        app.dependency_overrides.pop(rate_limit_contact, None)
    except ImportError:
        pass
