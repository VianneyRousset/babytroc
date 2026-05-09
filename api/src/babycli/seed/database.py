from contextlib import AbstractAsyncContextManager
from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .config import get_config


class SharedSession(AbstractAsyncContextManager):
    """Ensure a shared async sql session."""

    def __init__(self):
        config = get_config()
        engine = create_async_engine(
            config.database.url,
            echo=False,
        )
        self.sessionmaker = async_sessionmaker(
            bind=engine,
        )
        self.active_session = None
        self.active_context: AsyncSession | None = None
        self.clients = 0

    async def __aenter__(self) -> AsyncSession:
        # ensure active session
        if self.active_session is None:
            self.active_session = self.sessionmaker.begin()
            self.active_context = await self.active_session.__aenter__()

        # increment clients count
        self.clients = self.clients + 1

        return self.active_context  # type: ignore[return-value]

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool | None:
        # decrement clients count
        self.clients = self.clients - 1

        # end active session
        if self.clients == 0 and self.active_session:
            await self.active_session.__aexit__(exc_type, exc_val, exc_tb)
            self.active_session = None
            self.active_context = None

        return None


shared_session = SharedSession()
