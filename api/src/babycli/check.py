# babycli/check.py
import os
import sys

import httpx
from cyclopts import App

from ._utils import async_db_session, console_err, console_ok

check_app = App(
    name="check",
    help="Run health checks on external services.",
)


async def check_postgres() -> bool:
    try:
        from sqlalchemy import text as sa_text

        async with async_db_session() as session:
            result = await session.execute(sa_text("SELECT version()"))
            version = result.scalar()
            console_ok(f"PostgreSQL — {version}")
            return True
    except Exception as e:
        console_err(f"PostgreSQL — {e}")
        return False


async def check_redis() -> bool:
    try:
        from babytroc.infrastructure.config import RedisConfig
        from babytroc.infrastructure.redis import create_redis_client

        config = RedisConfig.from_env()
        client = create_redis_client(config)
        pong = await client.ping()
        await client.aclose()
        if pong:
            console_ok(f"Redis — pong ({config.host}:{config.port})")
            return True
        console_err("Redis — no pong")
        return False
    except Exception as e:
        console_err(f"Redis — {e}")
        return False


async def check_s3() -> bool:
    try:
        import aioboto3
        import botocore

        from babytroc.infrastructure.config import S3Config

        config = S3Config.from_env()
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


def check_email_config() -> bool:
    required = [
        "EMAIL_SERVER",
        "EMAIL_PORT",
        "EMAIL_USERNAME",
        "EMAIL_PASSWORD",
        "EMAIL_FROM_EMAIL",
        "EMAIL_FROM_NAME",
        "CONTACT_EMAIL",
    ]
    missing = [k for k in required if k not in os.environ]
    if missing:
        console_err(f"Email config — missing: {', '.join(missing)}")
        return False
    console_ok("Email config — all vars present")
    return True


async def check_migrations() -> bool:
    try:
        from alembic.config import Config as AlembicConfig
        from alembic.runtime.migration import MigrationContext
        from alembic.script import ScriptDirectory
        from sqlalchemy.engine import Connection
        from sqlalchemy.ext.asyncio import create_async_engine

        from babytroc.infrastructure.config import Config

        def _get_current_rev(conn: Connection) -> str | None:
            return MigrationContext.configure(conn).get_current_revision()

        config = Config.from_env()
        engine = create_async_engine(config.database.url)
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


async def check_cap() -> bool:
    try:
        from babytroc.infrastructure.config import CapConfig

        config = CapConfig.from_env()
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.get(f"{config.api_url}/", timeout=5.0)
        console_ok(f"Cap — reachable ({config.api_url})")
        return True
    except Exception as e:
        console_err(f"Cap — {e}")
        return False


@check_app.default
async def check_all():
    """Run all health checks."""
    results = [
        await check_postgres(),
        await check_redis(),
        await check_s3(),
        check_email_config(),
        await check_migrations(),
        await check_cap(),
    ]
    if not all(results):
        sys.exit(1)


@check_app.command(name="postgres")
async def check_postgres_cmd():
    """Check PostgreSQL connection."""
    if not await check_postgres():
        sys.exit(1)


@check_app.command(name="redis")
async def check_redis_cmd():
    """Check Redis connection."""
    if not await check_redis():
        sys.exit(1)


@check_app.command(name="s3")
async def check_s3_cmd():
    """Check S3/MinIO bucket."""
    if not await check_s3():
        sys.exit(1)


@check_app.command(name="email")
def check_email_cmd():
    """Check email configuration."""
    if not check_email_config():
        sys.exit(1)


@check_app.command(name="migrations")
async def check_migrations_cmd():
    """Check if database migrations are up to date."""
    if not await check_migrations():
        sys.exit(1)


@check_app.command(name="cap")
async def check_cap_cmd():
    """Check cap captcha server reachability."""
    if not await check_cap():
        sys.exit(1)
