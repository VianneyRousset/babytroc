from datetime import timedelta
from unittest.mock import patch

import pytest

from babytroc.infrastructure.config import (
    CapConfig,
    Config,
    ContactConfig,
    RateLimitConfig,
)


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


class TestConfigRateLimits:
    def test_config_has_per_endpoint_rate_limits(self):
        # Drop all overrides so defaults flow through.
        env: dict = {}
        # Provide every required env var so Config.from_env can build.
        env.update({
            "POSTGRES_USER": "u",
            "POSTGRES_PASSWORD": "p",
            "POSTGRES_HOST": "h",
            "POSTGRES_PORT": "5432",
            "POSTGRES_DATABASE": "d",
            "EMAIL_SERVER": "s",
            "EMAIL_PORT": "25",
            "EMAIL_USERNAME": "u",
            "EMAIL_PASSWORD": "p",
            "EMAIL_FROM_EMAIL": "a@b.c",
            "EMAIL_FROM_NAME": "X",
            "S3_ENDPOINT_URL": "http://s",
            "S3_ACCESS_KEY": "a",
            "S3_SECRET_KEY": "s",
            "S3_BUCKET": "b",
            "S3_PUBLIC_URL": "http://p",
            "JWT_ALGORITHM": "HS256",
            "JWT_SECRET_KEY": "k",
            "JWT_REFRESH_TOKEN_DURATION_DAYS": "7",
            "JWT_ACCESS_TOKEN_DURATION_MINUTES": "15",
            "ACCOUNT_PASSWORD_RESET_AUTHORIZATION_DURATION_MINUTES": "15",
            "HOST_NAME": "example.com",
            "APP_NAME": "BabyTroc",
            "CONTACT_EMAIL": "x@y.z",
            "CAP_API_URL": "http://cap",
            "CAP_SITE_KEY": "k",
            "CAP_SECRET_KEY": "s",
        })
        with patch.dict("os.environ", env, clear=True):
            cfg = Config.from_env()
        assert cfg.signup.anon == 3
        assert cfg.signup.auth == 3
        assert cfg.password_reset.anon == 3
        assert cfg.password_reset.auth == 3
        assert cfg.item_create.anon == 30
        assert cfg.item_create.auth == 30
        assert cfg.image_upload.anon == 60
        assert cfg.image_upload.auth == 60
