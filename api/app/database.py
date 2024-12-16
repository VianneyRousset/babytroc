from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


def create_session_maker(db_url: str) -> async_sessionmaker:
    engine = create_async_engine(db_url, echo=True)

    return async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )


async def get_session(request: Request) -> AsyncSession:
    async with request.app.state.db_session_maker.begin() as session:
        yield session
