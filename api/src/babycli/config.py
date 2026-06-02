# babycli/config.py
import os
import sys

from cyclopts import App

from ._utils import console_err, console_ok, redact_secrets

config_app = App(
    name="config",
    help="Show and validate configuration.",
)

REQUIRED_ENV_VARS = [
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "POSTGRES_DATABASE",
    "EMAIL_SERVER",
    "EMAIL_PORT",
    "EMAIL_USERNAME",
    "EMAIL_PASSWORD",
    "EMAIL_FROM_EMAIL",
    "EMAIL_FROM_NAME",
    "S3_ENDPOINT_URL",
    "S3_ACCESS_KEY",
    "S3_SECRET_KEY",
    "S3_BUCKET",
    "S3_PUBLIC_URL",
    "JWT_ALGORITHM",
    "JWT_SECRET_KEY",
    "JWT_REFRESH_TOKEN_DURATION_DAYS",
    "JWT_ACCESS_TOKEN_DURATION_MINUTES",
    "ACCOUNT_PASSWORD_RESET_AUTHORIZATION_DURATION_MINUTES",
    "HOST_NAME",
    "APP_NAME",
]

OPTIONAL_ENV_VARS = [
    "DELAY",
    "REDIS_URL",
    "REDIS_HOST",
    "REDIS_PORT",
    "REDIS_DB",
    "REDIS_PASSWORD",
]


@config_app.command(name="show")
def show():
    """Show resolved configuration (secrets redacted)."""
    print("=== Required ===")
    for key in REQUIRED_ENV_VARS:
        value = os.environ.get(key)
        if value is not None:
            print(f"  {key} = {redact_secrets(key, value)}")
        else:
            print(f"  {key} = (not set)")

    print("\n=== Optional ===")
    for key in OPTIONAL_ENV_VARS:
        value = os.environ.get(key)
        if value is not None:
            print(f"  {key} = {redact_secrets(key, value)}")
        else:
            print(f"  {key} = (default)")


@config_app.command(name="validate")
def validate():
    """Check all required environment variables are present."""
    missing = [k for k in REQUIRED_ENV_VARS if k not in os.environ]
    if missing:
        console_err(f"Missing {len(missing)} required env var(s):")
        for k in missing:
            print(f"  - {k}")
        sys.exit(1)
    else:
        console_ok(f"All {len(REQUIRED_ENV_VARS)} required env vars present")
