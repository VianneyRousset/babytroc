import abc
from collections.abc import Iterable
from itertools import zip_longest
from typing import Any, TypeVar

from pydantic import AliasChoices, BaseModel, ConfigDict, Field
from sqlalchemy import Delete, Select, Update
from sqlalchemy.orm import DeclarativeBase as SQLDeclarativeBase

StatementT = TypeVar("StatementT", Select, Update, Delete)


def FieldWithAlias(  # noqa: N802
    name: str,
    alias: str,
    *args,
    **kwargs,
) -> Any:
    return Field(
        *args,
        alias=alias,
        validation_alias=AliasChoices(name, alias),
        serialization_alias=alias,
        **kwargs,
    )


def PageLimitField(  # noqa: N802
    name="limit",
    alias="n",
    *,
    nmax=256,
) -> Any:
    return FieldWithAlias(
        name=name,
        alias=alias,
        gt=0,
        le=nmax,
        title="Limit results count",
        description="Limit the number of results.",
    )


class Base(BaseModel, abc.ABC):
    model_config = ConfigDict(
        from_attributes=True,
    )


class CreateBase(Base, extra="forbid"):
    pass


class ReadBase(Base):
    pass


class UpdateBase(Base, extra="forbid"):
    pass


class DeleteBase(Base, extra="forbid"):
    pass


class NetworkingBase(Base):
    pass


class Joins(tuple[type[SQLDeclarativeBase]]):
    def __new__(cls, joins: Iterable[type[SQLDeclarativeBase]] | None = None):
        return tuple.__new__(Joins, joins if joins is not None else [])

    def __add__(self, joins):
        return Joins(self._iter_merged(self, joins))

    def _iter_merged(
        self,
        a: Iterable[type[SQLDeclarativeBase]],
        b: Iterable[type[SQLDeclarativeBase]],
    ):
        for i, j in zip_longest(a, b):
            if i is None:
                yield j

            elif j is None:
                yield i

            elif i != j:
                msg = f"Incompatible joins {a} and {b}"
                raise ValueError(msg)

            else:
                yield i


# this filtering approach might have some limitation with complex filters
class QueryFilterBase(Base):
    def _filter(self, stmt: StatementT) -> StatementT:
        return stmt

    @property
    def key(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True)


class ReadQueryFilter(QueryFilterBase):
    @property
    def joins(self) -> Joins:
        return self._joins

    @property
    def _joins(self) -> Joins:
        return Joins()

    def filter_read(self, stmt: Select) -> Select:
        # apply joins
        for join in self.joins:
            stmt = stmt.join(join)

        return self._filter_read(stmt)

    def _filter_read(self, stmt: Select) -> Select:
        return self._filter(stmt)


class UpdateQueryFilter(QueryFilterBase):
    def filter_update(self, stmt: Update) -> Update:
        return self._filter_update(stmt)

    def _filter_update(self, stmt: Update) -> Update:
        return self._filter(stmt)


class DeleteQueryFilter(QueryFilterBase):
    def filter_delete(self, stmt: Delete) -> Delete:
        return self._filter_delete(stmt)

    def _filter_delete(self, stmt: Delete) -> Delete:
        return self._filter(stmt)


class QueryFilter(
    ReadQueryFilter,
    UpdateQueryFilter,
    DeleteQueryFilter,
):
    pass


class ApiQueryBase(Base, extra="forbid"):
    pass
