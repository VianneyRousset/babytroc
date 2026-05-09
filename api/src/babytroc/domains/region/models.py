from sqlalchemy import (
    Identity,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from babytroc.shared.models import Base


class Region(Base):
    __tablename__ = "region"

    id: Mapped[int] = mapped_column(
        Integer,
        Identity(),
        primary_key=True,
        index=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String,
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} #{self.id!r} {self.name!r}>"
