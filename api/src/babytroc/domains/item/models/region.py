from sqlalchemy import (
    ForeignKey,
    Integer,
)
from sqlalchemy.orm import Mapped, mapped_column

from babytroc.shared.models import Base


class ItemRegionAssociation(Base):
    """Items and regions association table"""

    __tablename__ = "item_region_association"

    item_id = mapped_column(
        Integer,
        ForeignKey(
            "item.id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        primary_key=True,
    )

    region_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "region.id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        primary_key=True,
    )
