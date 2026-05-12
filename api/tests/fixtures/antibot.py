from collections.abc import AsyncGenerator, Callable
from datetime import timedelta
from typing import Any

import pytest
from fastapi import FastAPI

from babytroc.infrastructure import cap as cap_module
from babytroc.shared import antibot as antibot_module
from babytroc.shared.rate_limit import RateLimiter


@pytest.fixture
def cap_verify_result() -> bool:
    """Override via `@pytest.mark.parametrize` to return False from the cap stub."""
    return True


@pytest.fixture
def cap_verify_raises() -> bool:
    """Override to True to make the stub return False (simulating cap-unreachable
    after the fail-closed exception handling in `verify_cap_token`)."""
    return False


@pytest.fixture(autouse=True)
def stub_cap_verify(
    monkeypatch: pytest.MonkeyPatch,
    cap_verify_result: bool,
    cap_verify_raises: bool,
):
    """Replace `verify_cap_token` everywhere it has been imported.

    `shared/antibot.py` does `from babytroc.infrastructure.cap import verify_cap_token`,
    so we patch both modules.
    """

    async def _fake(_config, _token):
        if cap_verify_raises:
            # `verify_cap_token` is fail-closed: it catches httpx errors
            # internally and returns False. Simulate that contract here.
            return False
        return cap_verify_result

    monkeypatch.setattr(cap_module, "verify_cap_token", _fake)
    monkeypatch.setattr(antibot_module, "verify_cap_token", _fake)


@pytest.fixture
def tight_rate_limit_factory(app: FastAPI) -> Callable[..., Any]:
    """Return a function that overrides one endpoint's rate-limit dep with
    tight values so rate-limit tests run fast.

    Usage:
        from babytroc.routers.v1.utils.contact import rate_limit_contact
        tight_rate_limit_factory(
            dep=rate_limit_contact,
            key_prefix="contact-test",
            anon_limit=2, auth_limit=3, window_seconds=60,
        )
    """

    def _set(
        *,
        dep: Callable[..., Any],
        key_prefix: str,
        anon_limit: int,
        auth_limit: int,
        window_seconds: int,
    ) -> None:
        new = RateLimiter(
            key_prefix=key_prefix,
            anon_limit=anon_limit,
            auth_limit=auth_limit,
            window=timedelta(seconds=window_seconds),
        )
        app.dependency_overrides[dep] = new

    return _set


@pytest.fixture(autouse=True)
async def _clear_rate_limit_state(app: FastAPI) -> AsyncGenerator[None]:
    """Clear any rate-limit dep overrides set during the test, plus any cached
    limiter instances stashed on `app.state` (so default-limit tests start
    fresh between runs).
    """
    yield
    # Pop only the rate-limit deps we know about, to avoid touching unrelated
    # overrides other tests may set.
    try:
        from babytroc.routers.v1.utils.contact import rate_limit_contact
        app.dependency_overrides.pop(rate_limit_contact, None)
    except ImportError:
        pass
    for attr in [a for a in vars(app.state) if a.startswith("_rate_limiter_")]:
        delattr(app.state, attr)
