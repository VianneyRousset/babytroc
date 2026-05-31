# babycli/check.py
import sys
from typing import TYPE_CHECKING, cast

import httpx
from cyclopts import App

if TYPE_CHECKING:
    from collections.abc import Awaitable

from ._utils import async_db_session, console_err, console_ok

check_app = App(
    name="check",
    help="Run health checks on external services.",
)


async def check_postgres(*, test: bool | None = None) -> bool:
    try:
        from sqlalchemy import text as sa_text

        async with async_db_session(test=test) as session:
            result = await session.execute(sa_text("SELECT version()"))
            version = result.scalar()
            console_ok(f"PostgreSQL — {version}")
            return True
    except Exception as e:
        console_err(f"PostgreSQL — {e}")
        return False


async def check_redis(*, test: bool | None = None) -> bool:
    try:
        from babytroc.infrastructure.config import RedisConfig
        from babytroc.infrastructure.redis import create_redis_client

        config = RedisConfig.from_env(test=test)
        client = create_redis_client(config)
        pong = await cast("Awaitable[bool]", client.ping())
        await client.aclose()
        if pong:
            console_ok(f"Redis — pong ({config.host}:{config.port})")
            return True
        console_err("Redis — no pong")
        return False
    except Exception as e:
        console_err(f"Redis — {e}")
        return False


async def check_s3(*, test: bool | None = None) -> bool:
    try:
        import aioboto3
        import botocore

        from babytroc.infrastructure.config import S3Config

        config = S3Config.from_env(test=test)
        s3_session = aioboto3.Session()
        async with s3_session.client(
            "s3",
            endpoint_url=config.endpoint_url,
            aws_access_key_id=config.access_key,
            aws_secret_access_key=config.secret_key,
        ) as client:
            try:
                await client.head_bucket(Bucket=config.bucket)

            except botocore.exceptions.ClientError as e:
                if e.response.get("Error", {}).get("Code") != "404":
                    raise e
                console_err(f"S3 — Missing bucket {config.bucket!r}")
                return False

            console_ok(f"S3 — bucket '{config.bucket}' exists ({config.endpoint_url})")
            return True
    except Exception as e:
        console_err(f"S3 — {e}")
        return False


async def check_email_connection(*, test: bool | None = None) -> bool:

    try:
        from fastapi_mail import ConnectionConfig as EmailConnectionConfig
        from fastapi_mail.connection import Connection

        from babytroc.infrastructure.config import EmailConfig

        config = EmailConfig.from_env(test=test)
        connection = Connection(
            EmailConnectionConfig(
                MAIL_USERNAME=config.username,
                MAIL_PASSWORD=config.password,
                MAIL_PORT=config.port,
                MAIL_SERVER=config.server,
                MAIL_FROM=config.from_email,
                MAIL_FROM_NAME=config.from_name,
                MAIL_STARTTLS=False,
                MAIL_SSL_TLS=True,
                USE_CREDENTIALS=True,
                VALIDATE_CERTS=True,
            )
        )

        async with connection:
            pass

    except Exception as e:
        console_err(f"Email connection — {e}")
        return False
    console_ok("Email connection — established")
    return True


async def check_migrations(*, test: bool | None = None) -> bool:
    try:
        from alembic.config import Config as AlembicConfig
        from alembic.runtime.migration import MigrationContext
        from alembic.script import ScriptDirectory
        from sqlalchemy.engine import Connection
        from sqlalchemy.ext.asyncio import create_async_engine

        from babytroc.infrastructure.config import DatabaseConfig

        def _get_current_rev(conn: Connection) -> str | None:
            return MigrationContext.configure(conn).get_current_revision()

        config = DatabaseConfig.from_env(test=test)
        engine = create_async_engine(config.url)
        try:
            async with engine.connect() as conn:
                current_rev = await conn.run_sync(_get_current_rev)
        finally:
            await engine.dispose()

        alembic_cfg = AlembicConfig("alembic.ini")
        script = ScriptDirectory.from_config(alembic_cfg)
        head_rev = script.get_current_head()

        if current_rev == head_rev:
            console_ok(f"Migrations — up to date ({current_rev})")
            return True
        console_err(
            f"Migrations — out of date - current: {current_rev}, head: {head_rev}"
        )
        return False
    except Exception as e:
        console_err(f"Migrations — {e}")
        return False


async def check_cap(*, test: bool | None = None) -> bool:
    try:
        from babytroc.infrastructure.config import CapConfig

        config = CapConfig.from_env(test=test)
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.get(f"{config.api_url}/", timeout=5.0)
        console_ok(f"Cap — reachable ({config.api_url})")
        return True
    except Exception as e:
        console_err(f"Cap — {e}")
        return False


@check_app.default
async def check_all(*, test: bool | None = None):
    """Run all health checks."""

    if test:
        results = [
            await check_postgres(test=test),
            await check_redis(test=test),
        ]
    else:
        results = [
            await check_postgres(test=test),
            await check_redis(test=test),
            await check_s3(test=test),
            await check_email_connection(test=test),
            await check_migrations(test=test),
            await check_cap(test=test),
        ]

    if not all(results):
        sys.exit(1)


@check_app.command(name="postgres")
async def check_postgres_cmd(*, test: bool | None = None):
    """Check PostgreSQL connection."""
    if not await check_postgres(test=test):
        sys.exit(1)


@check_app.command(name="redis")
async def check_redis_cmd(*, test: bool | None = None):
    """Check Redis connection."""
    if not await check_redis(test=test):
        sys.exit(1)


@check_app.command(name="s3")
async def check_s3_cmd(*, test: bool | None = None):
    """Check S3/MinIO bucket."""
    if not await check_s3(test=test):
        sys.exit(1)


@check_app.command(name="email")
def check_email_cmd(*, test: bool | None = None):
    """Check email configuration."""
    if not check_email_connection(test=test):
        sys.exit(1)


@check_app.command(name="migrations")
async def check_migrations_cmd(*, test: bool | None = None):
    """Check if database migrations are up to date."""
    if not await check_migrations(test=test):
        sys.exit(1)


@check_app.command(name="cap")
async def check_cap_cmd(*, test: bool | None = None):
    """Check cap captcha server reachability."""
    if not await check_cap(test=test):
        sys.exit(1)
