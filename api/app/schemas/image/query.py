from typing import Annotated

from app.schemas.base import Base, FieldWithAlias


class ItemImageQuery(Base):
    size: Annotated[
        int | None,
        FieldWithAlias(
            name="size",
            alias="s",
            ge=16,
            le=1024,
        ),
    ]
