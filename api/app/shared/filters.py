"""Shared composable query filter helpers."""

from sqlalchemy import Select, desc, text


def order_by_newest(stmt: Select, column=None) -> Select:
    """Order by column descending (default: id)."""
    if column is not None:
        return stmt.order_by(desc(column))
    return stmt.order_by(text("id DESC"))


def paginate_by_id(
    stmt: Select, *, cursor_id: int | None = None, limit: int = 32
) -> Select:
    """Cursor-based keyset pagination using id.

    Fetches limit rows (caller handles +1 for next-page detection if needed).
    """
    if cursor_id is not None:
        stmt = stmt.where(text("id < :cursor_id")).params(cursor_id=cursor_id)
    return stmt.limit(limit)
