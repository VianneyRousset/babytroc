from datetime import timedelta
from unittest.mock import patch

import pytest

from babytroc.infrastructure.config import CapConfig, ContactConfig, RateLimitConfig


class TestContactConfig:
    def test_from_env_with_all_vars(self):
        env = {
            "CONTACT_EMAIL": "contact@babytroc.ch",
            "CONTACT_RATE_LIMIT_ANON": "3",
            "CONTACT_RATE_LIMIT_AUTH": "8",
            "CONTACT_RATE_LIMIT_WINDOW_SECONDS": "600",
        }
        with patch.dict("os.environ", env, clear=True):
            cfg = ContactConfig.from_env()
        assert cfg.email == "contact@babytroc.ch"
        assert cfg.rate_limit.anon == 3
        assert cfg.rate_limit.auth == 8
        assert cfg.rate_limit.window == timedelta(seconds=600)

    def test_from_env_uses_defaults(self):
        env = {"CONTACT_EMAIL": "contact@babytroc.ch"}
        with patch.dict("os.environ", env, clear=True):
            cfg = ContactConfig.from_env()
        assert cfg.rate_limit.anon == 5
        assert cfg.rate_limit.auth == 10
        assert cfg.rate_limit.window == timedelta(seconds=3600)

    def test_from_env_requires_email(self):
        with patch.dict("os.environ", {}, clear=True), pytest.raises(KeyError):
            ContactConfig.from_env()


class TestCapConfig:
    def test_from_env_with_all_vars(self):
        env = {
            "CAP_API_URL": "https://cap.example.com",
            "CAP_SITE_KEY": "site-123",
            "CAP_SECRET_KEY": "secret-xyz",
        }
        with patch.dict("os.environ", env, clear=True):
            cfg = CapConfig.from_env()
        assert cfg.api_url == "https://cap.example.com"
        assert cfg.site_key == "site-123"
        assert cfg.secret_key == "secret-xyz"

    def test_from_env_requires_all_vars(self):
        with patch.dict("os.environ", {}, clear=True), pytest.raises(KeyError):
            CapConfig.from_env()


class TestRateLimitConfig:
    def test_from_env_uses_defaults_when_unset(self):
        with patch.dict("os.environ", {}, clear=True):
            cfg = RateLimitConfig.from_env(
                env_prefix="SIGNUP",
                default_anon=3, default_auth=3, default_window_seconds=3600,
            )
        assert cfg.anon == 3
        assert cfg.auth == 3
        assert cfg.window == timedelta(seconds=3600)

    def test_from_env_reads_env_overrides(self):
        env = {
            "SIGNUP_RATE_LIMIT_ANON": "7",
            "SIGNUP_RATE_LIMIT_AUTH": "11",
            "SIGNUP_RATE_LIMIT_WINDOW_SECONDS": "120",
        }
        with patch.dict("os.environ", env, clear=True):
            cfg = RateLimitConfig.from_env(
                env_prefix="SIGNUP",
                default_anon=3, default_auth=3, default_window_seconds=3600,
            )
        assert cfg.anon == 7
        assert cfg.auth == 11
        assert cfg.window == timedelta(seconds=120)
