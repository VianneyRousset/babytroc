from collections.abc import Collection
from typing import Any, Literal, Optional, Union

from sqlalchemy import Select
from sqlalchemy.orm import (
    ColumnProperty,
    InstrumentedAttribute,
    QueryableAttribute,
    RelationshipProperty,
    selectinload,
    undefer,
)
from sqlalchemy.sql.base import ExecutableOption

LoadableAttrType = Union[Literal["*"], QueryableAttribute[Any]]


def add_default_query_options(
    stmt: Select,
    *,
    load_attributes: Optional[Collection[LoadableAttrType]] = None,
    options: Optional[Collection[ExecutableOption]] = None,
) -> Select:
    """Add a `selectinload()` option to the `select()` for each `loaded_attrs`."""

    for attr in load_attributes or []:
        if isinstance(attr, InstrumentedAttribute):
            if isinstance(attr.property, RelationshipProperty):
                stmt = stmt.options(selectinload(attr))
            elif isinstance(attr.property, ColumnProperty):
                stmt = stmt.options(undefer(attr))
            else:
                msg = (
                    f"Unexpected attribute property type for {attr!r}: "
                    f"({type(attr.property)!r})."
                )
                raise TypeError(msg)

        elif isinstance(attr, str) and attr == "*":
            stmt = stmt.options(selectinload(attr))

        else:
            msg = f"Unexpected attribute type: {type(attr)!r}."
            raise TypeError(msg)

    for option in options or []:
        stmt = stmt.options(option)

    return stmt
