from contextlib import AbstractContextManager
from types import TracebackType

import sqlalchemy

from .config import get_config


class SharedSession(AbstractContextManager):
    """Ensure a shared sql session."""

    def __init__(self):
        config = get_config()
        engine = sqlalchemy.create_engine(
            config.database.url,
            echo=False,
        )
        self.sessionmaker = sqlalchemy.orm.sessionmaker(
            bind=engine,
            autoflush=False,
        )
        self.active_session = None
        self.active_context = None
        self.clients = 0

    def __enter__(self):
        # ensure active session
        if self.active_session is None:
            self.active_session = self.sessionmaker.begin()
            self.active_context = self.active_session.__enter__()

        # increment clients count
        self.clients = self.clients + 1

        return self.active_context

    def __exit__(
        self,
        type: type[BaseException] | None,
        value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        # decrement clients count
        self.clients = self.clients - 1

        # end active session
        if self.clients == 0 and self.active_session:
            self.active_session.__exit__(type, value, traceback)

        return None


shared_session = SharedSession()
