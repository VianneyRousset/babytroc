# babycli/setup.py
import os
import sys
from typing import Annotated

from cyclopts import App, Parameter

from ._utils import console_err, console_ok, console_warn
from .check import check_email_config, check_migrations, check_postgres, check_redis, check_s3
from .config import REQUIRED_ENV_VARS

setup_app = App(
    name="setup",
    help="Guided setup wizard for new installations.",
)

_POSTGRES_HINTS = """
  Install PostgreSQL:
    apt:    sudo apt install postgresql
    brew:   brew install postgresql@16
    docker: docker run -d --name postgres -e POSTGRES_PASSWORD=babytroc -p 5432:5432 postgres:16

  Required env vars:
    POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DATABASE
"""

_REDIS_HINTS = """
  Install Redis:
    apt:    sudo apt install redis-server
    brew:   brew install redis
    docker: docker run -d --name redis -p 6379:6379 redis:7

  Optional env vars (defaults: localhost:6379/0):
    REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD
"""

_S3_HINTS = """
  Install MinIO (S3-compatible):
    docker: docker run -d --name minio -p 9000:9000 -p 9001:9001 \\
              -e MINIO_ROOT_USER=minioadmin -e MINIO_ROOT_PASSWORD=minioadmin \\
              minio/minio server /data --console-address ":9001"

  Required env vars:
    S3_ENDPOINT_URL, S3_ACCESS_KEY, S3_SECRET_KEY, S3_BUCKET, S3_PUBLIC_URL
"""

_EMAIL_HINTS = """
  Required env vars:
    EMAIL_SERVER, EMAIL_PORT, EMAIL_USERNAME, EMAIL_PASSWORD,
    EMAIL_FROM_EMAIL, EMAIL_FROM_NAME

  For dev, use a service like Mailtrap or maildev:
    docker: docker run -d --name maildev -p 1080:1080 -p 1025:1025 maildev/maildev
"""


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

    all_ok = True

    # Step 1: Environment variables
    print("  Step 1: Environment Variables")
    missing = [k for k in REQUIRED_ENV_VARS if k not in os.environ]
    if missing:
        console_err(f"{len(missing)} required env var(s) missing:")
        for k in missing:
            print(f"    - {k}")
        all_ok = False
    else:
        console_ok(f"All {len(REQUIRED_ENV_VARS)} required env vars present")

    if missing and not check_only:
        print("\n  Set them in your .env.yaml or environment before continuing.")
        print("  Run 'babycli config show' to inspect current values.\n")

    # Step 2: PostgreSQL
    print("  Step 2: PostgreSQL")
    if not await check_postgres():
        all_ok = False
        if not check_only:
            print(_POSTGRES_HINTS)

    # Step 3: Redis
    print("  Step 3: Redis")
    if not await check_redis():
        all_ok = False
        if not check_only:
            print(_REDIS_HINTS)

    # Step 4: S3/MinIO
    print("  Step 4: S3 / MinIO")
    if not await check_s3():
        all_ok = False
        if not check_only:
            print(_S3_HINTS)

    # Step 5: Email
    print("  Step 5: Email")
    if not check_email_config():
        all_ok = False
        if not check_only:
            print(_EMAIL_HINTS)

    # Step 6: Migrations
    print("  Step 6: Alembic Migrations")
    if not await check_migrations():
        all_ok = False
        if not check_only:
            console_warn("Run 'babycli db migrate' to apply pending migrations.")

    # Summary
    print("\n  ========================")
    if all_ok:
        console_ok("All checks passed! Run 'babycli server start' to begin.")
    else:
        console_err("Some checks failed. Fix the issues above and re-run 'babycli setup'.")
        if check_only:
            sys.exit(1)
