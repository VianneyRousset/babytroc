from datetime import datetime

from sqlalchemy import DateTime, Identity, Integer, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class IntegerIdentifier:
    id: Mapped[int] = mapped_column(
        Integer,
        Identity(always=True),
        primary_key=True,
        index=True,
        autoincrement=True,
    )


class CreationDate:
    creation_date: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )
