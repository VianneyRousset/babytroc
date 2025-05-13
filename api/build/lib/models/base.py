from datetime import datetime

from sqlalchemy import DateTime, Identity, Integer, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql.functions import GenericFunction


class NormalizeText(GenericFunction):
    type = Text()
    name = "normalize_text"
    inherit_cache = True


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


# TODO check for proper UTC datetime management


class CreationDate:
    creation_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


class UpdateDate:
    update_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
