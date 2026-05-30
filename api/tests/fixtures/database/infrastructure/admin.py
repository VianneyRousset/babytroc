"""PostgreSQL admin helpers — CREATE/DROP DATABASE, ALTER ALLOW_CONNECTIONS."""

from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

from sqlalchemy import URL, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool


async def create_database(
    url: URL,
    *,
    admin_url: URL,
    encoding: str = "utf8",
    template: str | None = None,
) -> None:
    """`CREATE DATABASE url.database TEMPLATE template`. Defaults to template1.

    `admin_url` must point to an existing database (typically the cluster's
    `postgres` admin db) — CREATE DATABASE cannot be issued from a connection
    to a database that does not yet exist.
    """
    database = url.database
    if database is None:
        msg = "url.database must be set"
        raise ValueError(msg)

    engine = create_async_engine(
        admin_url,
        isolation_level="AUTOCOMMIT",
        poolclass=NullPool,
    )
    try:
        async with engine.begin() as conn:
            await conn.execute(
                text(
                    f'CREATE DATABASE "{database}" '
                    f"ENCODING '{encoding}' "
                    f'TEMPLATE "{template or "template1"}"',
                ),
            )
    finally:
        await engine.dispose()


async def drop_database(url: URL, *, admin_url: URL) -> None:
    """`DROP DATABASE url.database` issued from `admin_url`."""
    database = url.database
    if database is None:
        msg = "url.database must be set"
        raise ValueError(msg)

    engine = create_async_engine(
        admin_url,
        isolation_level="AUTOCOMMIT",
        poolclass=NullPool,
    )
    try:
        async with engine.begin() as conn:
            await conn.execute(text(f'DROP DATABASE "{database}"'))
    finally:
        await engine.dispose()


async def set_datallowconn(url: URL, *, allow: bool) -> None:
    """ALTER DATABASE WITH ALLOW_CONNECTIONS = …."""
    database = url.database
    if database is None:
        msg = "url.database must be set"
        raise ValueError(msg)

    engine = create_async_engine(
        url,
        isolation_level="AUTOCOMMIT",
        poolclass=NullPool,
    )
    try:
        async with engine.begin() as conn:
            val = "true" if allow else "false"
            await conn.execute(
                text(f'ALTER DATABASE "{database}" WITH ALLOW_CONNECTIONS = {val}'),
            )
    finally:
        await engine.dispose()


@asynccontextmanager
async def session_against(url: URL) -> AsyncIterator[AsyncSession]:
    """Open a session against `url`, yield it inside a transaction, dispose engine.

    Dispose runs in finally so no connections survive — required before any
    downstream `CREATE DATABASE … TEMPLATE` of this URL.
    """
    engine = create_async_engine(url=url, echo=False, poolclass=NullPool)
    maker = async_sessionmaker(bind=engine)
    try:
        async with maker.begin() as session:
            yield session
    finally:
        await engine.dispose()


async def run_against[T](
    url: URL,
    fn: Callable[[AsyncSession], Awaitable[T]],
) -> T:
    """Run `fn(session)` inside a transaction against `url` and dispose engine."""
    async with session_against(url) as session:
        return await fn(session)
