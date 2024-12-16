from collections.abc import Collection

from sqlalchemy import Select
from sqlalchemy.orm import selectinload


def load_relationships(
    stmt: Select,
    *,
    entity,
    load_relationships: Collection[str],
) -> Select:
    """Add a `selectinload()` option to the `select()` for each `loaded_attrs`."""

    for attrname in load_relationships or []:
        if attrname != "*":
            attrname = getattr(entity, attrname)

        stmt = stmt.options(selectinload(attrname))

    return stmt
