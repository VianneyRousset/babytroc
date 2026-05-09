import warnings
from collections.abc import AsyncGenerator

from sqlalchemy import URL
from sqlalchemy.exc import SAWarning
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# make sqlalchemy warnings as errors
warnings.simplefilter("error", SAWarning)


def create_session_maker(db_url: URL, **engine_kwargs) -> async_sessionmaker:
    engine = create_async_engine(
        url=db_url,
        echo=False,
        **engine_kwargs,
    )

    return async_sessionmaker(
        bind=engine,
    )


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    async with _session_maker.begin() as session:
        yield session
    # Flush pub/sub notifications after the transaction has committed
    # (data is now visible to other connections)
    from babytroc.infrastructure.pubsub import flush_pending_notifications

    await flush_pending_notifications(session)


_session_maker: async_sessionmaker


def get_session_maker() -> async_sessionmaker:
    return _session_maker


def init_db_session_dependency(session_maker: async_sessionmaker) -> None:
    global _session_maker
    _session_maker = session_maker
