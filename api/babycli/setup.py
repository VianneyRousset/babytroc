import os
import sys
from typing import Annotated

from cyclopts import App, Parameter

from ._utils import console_err, console_ok, console_warn
from .check import (
    check_email_config,
    check_migrations,
    check_postgres,
    check_redis,
    check_s3,
)
from .config import REQUIRED_ENV_VARS

setup_app = App(
    name="setup",
    help="Guided setup wizard for new installations.",
)

_POSTGRES_HINTS = """\
  Install PostgreSQL:
    apt:    sudo apt install postgresql
    brew:   brew install postgresql@16
    docker: docker run -d --name postgres \\
              -e POSTGRES_PASSWORD=babytroc -p 5432:5432 postgres:16

  Required env vars:
    POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST,
    POSTGRES_PORT, POSTGRES_DATABASE"""

_REDIS_HINTS = """\
  Install Redis:
    apt:    sudo apt install redis-server
    brew:   brew install redis
    docker: docker run -d --name redis -p 6379:6379 redis:7

  Optional env vars (defaults: localhost:6379/0):
    REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD"""

_S3_HINTS = """\
  Install MinIO (S3-compatible):
    docker: docker run -d --name minio \\
              -p 9000:9000 -p 9001:9001 \\
              -e MINIO_ROOT_USER=minioadmin \\
              -e MINIO_ROOT_PASSWORD=minioadmin \\
              minio/minio server /data --console-address ":9001"

  Required env vars:
    S3_ENDPOINT_URL, S3_ACCESS_KEY, S3_SECRET_KEY,
    S3_BUCKET, S3_PUBLIC_URL"""

_EMAIL_HINTS = """\
  Required env vars:
    EMAIL_SERVER, EMAIL_PORT, EMAIL_USERNAME,
    EMAIL_PASSWORD, EMAIL_FROM_EMAIL, EMAIL_FROM_NAME

  For dev, use a service like Mailtrap or maildev:
    docker: docker run -d --name maildev \\
              -p 1080:1080 -p 1025:1025 maildev/maildev"""


async def _check_env_vars(check_only: bool) -> bool:
    print("  Step 1: Environment Variables")
    missing = [k for k in REQUIRED_ENV_VARS if k not in os.environ]
    if not missing:
        console_ok(f"All {len(REQUIRED_ENV_VARS)} required env vars present")
        return True
    console_err(f"{len(missing)} required env var(s) missing:")
    for k in missing:
        print(f"    - {k}")
    if not check_only:
        print("\n  Set them in .env.yaml or environment.")
        print("  Run 'babycli config show' to inspect.\n")
    return False


async def _run_service_check(
    step: str,
    label: str,
    check_fn,
    hints: str,
    check_only: bool,
) -> bool:
    print(f"  Step {step}: {label}")
    ok = await check_fn()
    if not ok and not check_only:
        print(hints)
    return ok


@setup_app.default
async def setup(
    check_only: Annotated[
        bool,
        Parameter(name="--check-only", help="Non-interactive, exit 0/1."),
    ] = False,
):
    """Run guided setup wizard."""
    print("\n  Babytroc API Setup Wizard")
    print("  ========================\n")

    results = [await _check_env_vars(check_only)]

    for step, label, fn, hints in [
        ("2", "PostgreSQL", check_postgres, _POSTGRES_HINTS),
        ("3", "Redis", check_redis, _REDIS_HINTS),
        ("4", "S3 / MinIO", check_s3, _S3_HINTS),
    ]:
        results.append(
            await _run_service_check(step, label, fn, hints, check_only),
        )

    # Email is sync
    print("  Step 5: Email")
    email_ok = check_email_config()
    if not email_ok and not check_only:
        print(_EMAIL_HINTS)
    results.append(email_ok)

    results.append(
        await _run_service_check(
            "6", "Alembic Migrations", check_migrations, "", check_only,
        ),
    )
    if not results[-1] and not check_only:
        console_warn("Run 'babycli db migrate' to apply pending migrations.")

    print("\n  ========================")
    if all(results):
        console_ok(
            "All checks passed! Run 'babycli server start' to begin.",
        )
    else:
        console_err(
            "Some checks failed. Fix issues above, re-run 'babycli setup'.",
        )
        if check_only:
            sys.exit(1)
