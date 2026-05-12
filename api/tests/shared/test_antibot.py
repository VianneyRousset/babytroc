import pytest
from pydantic import ValidationError

from babytroc.infrastructure.config import CapConfig
from babytroc.shared.antibot import AntiBotMixin, verify_antibot
from babytroc.shared.errors import BadRequestError

CAP_CONFIG = CapConfig(
    api_url="https://cap.example.com",
    site_key="site",
    secret_key="secret",
)


class _Payload(AntiBotMixin):
    """Composing schema used only to instantiate the mixin in tests."""


def _payload(*, cap_token: str = "pow_token", website: str = "") -> _Payload:  # noqa: S107
    return _Payload(cap_token=cap_token, website=website)


# --- mixin validation ---

def test_mixin_requires_cap_token():
    with pytest.raises(ValidationError):
        _Payload(website="")  # type: ignore[call-arg]


def test_mixin_website_defaults_to_empty():
    p = _Payload(cap_token="t")
    assert p.website == ""


def test_mixin_rejects_cap_token_too_long():
    with pytest.raises(ValidationError):
        _Payload(cap_token="x" * 4097)


# --- verify_antibot ---

async def test_verify_antibot_passes_when_clean(monkeypatch: pytest.MonkeyPatch):
    async def _ok(_config, _token):
        return True
    monkeypatch.setattr("babytroc.shared.antibot.verify_cap_token", _ok)
    await verify_antibot(_payload(), CAP_CONFIG)  # should not raise


async def test_verify_antibot_rejects_filled_honeypot():
    with pytest.raises(BadRequestError) as exc:
        await verify_antibot(_payload(website="x"), CAP_CONFIG)
    assert exc.value.message == "INVALID_SUBMISSION"


async def test_verify_antibot_rejects_when_cap_fails(monkeypatch: pytest.MonkeyPatch):
    async def _fail(_config, _token):
        return False
    monkeypatch.setattr("babytroc.shared.antibot.verify_cap_token", _fail)
    with pytest.raises(BadRequestError) as exc:
        await verify_antibot(_payload(), CAP_CONFIG)
    assert exc.value.message == "INVALID_SUBMISSION"


async def test_verify_antibot_runs_honeypot_before_cap(monkeypatch: pytest.MonkeyPatch):
    cap_called = False
    async def _spy(_config, _token):
        nonlocal cap_called
        cap_called = True
        return True
    monkeypatch.setattr("babytroc.shared.antibot.verify_cap_token", _spy)
    with pytest.raises(BadRequestError):
        await verify_antibot(_payload(website="x"), CAP_CONFIG)
    assert cap_called is False
