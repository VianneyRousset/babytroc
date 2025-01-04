from typing import Any, Generic, Optional, Self

from pydantic import Field, field_validator
from sqlalchemy import Select, tuple_
from sqlalchemy.sql.expression import ColumnExpressionArgument

from .base import QueryPageBase, ResultType


class QueryPageOptions(QueryPageBase):
    """Options on the queried page."""

    limit: Optional[int] = Field(gt=0, default=None)
    order: list[str] = Field(default=[])
    cursor: dict[str, Any] = Field(default={})
    desc: bool = Field(default=False)

    @field_validator("cursor")
    def validate_cursor(cls, cursor):  # noqa: N805
        return {k: v for k, v in cursor.items() if v is not None}

    def apply(
        self, stmt: Select, columns: dict[str, ColumnExpressionArgument]
    ) -> Select:
        stmt = self.apply_limit(stmt)
        stmt = self.apply_order(stmt, columns)
        return self.apply_cursor(stmt, columns)

    def apply_limit(self, stmt: Select) -> Select:
        if self.limit is not None:
            return stmt.limit(self.limit)

        return stmt

    def apply_order(
        self, stmt: Select, columns: dict[str, ColumnExpressionArgument]
    ) -> Select:
        if not self.order:
            return stmt

        cols = tuple_(
            *[columns[name] for name in self.order if columns[name] is not None]
        )

        if self.desc:
            return stmt.order_by(cols.desc())

        return stmt.order_by(cols)

    def apply_cursor(
        self, stmt: Select, columns: dict[str, ColumnExpressionArgument]
    ) -> Select:
        if not self.cursor:
            return stmt

        cols = tuple_(*[columns[name] for name in self.order if name in self.cursor])
        cursor = tuple_(
            *[self.cursor[name] for name in self.order if name in self.cursor]
        )

        if self.desc:
            return stmt.where(cols < cursor)

        return stmt.where(cols > cursor)


class QueryPageResult(QueryPageBase, Generic[ResultType]):
    """Info on the result page."""

    data: list[Any]
    order: dict[str, list[Any]]
    desc: bool = Field(default=False)

    @field_validator("order", mode="before")
    def validate_order(cls, order):  # noqa: N805
        return {k: v for k, v in order.items() if v}

    def next_cursor(self) -> dict[str, Any]:
        if not self.data:
            return {}

        comp = min if self.desc else max

        cursor = {}

        index = 0
        for k, v in self.order.items():
            cursor[k] = comp(v[index:])
            index = v.index(cursor[k])

        return cursor

    @property
    def total_count(self):
        return len(self.data)

    @classmethod
    def cast(cls, obj: Self, t: type[ResultType]) -> Self:
        return cls(
            **{
                **obj.model_dump(),
                "data": [t.model_validate(o) for o in obj.data],
            }
        )
