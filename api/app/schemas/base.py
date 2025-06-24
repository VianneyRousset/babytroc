import abc
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field
from sqlalchemy import Select


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


class QueryFilterBase(Base, extra="forbid"):
    @abc.abstractmethod
    def apply(self, stmt: Select) -> Select:
        raise NotImplementedError(repr(self.apply))

    @property
    def key(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True)


class ApiQueryBase(Base, extra="forbid"):
    pass
