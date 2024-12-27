import abc
from typing import Any, Generic, Self, Type, TypeVar

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Select

ResultType = TypeVar("ResultType")


class Base(BaseModel, Generic[ResultType], abc.ABC):
    # TODO move `from_attributes` to ReadBase only ?
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


class QueryFilterBase(Base, extra="forbid"):
    @abc.abstractmethod
    def apply(self, stmt: Select) -> Select:
        raise NotImplementedError(repr(self.apply))

    @property
    def key(self) -> dict[str, Any]:
        return self.dict(exclude_none=True)


class QueryPageOptionsBase(Base, extra="forbid"):
    @abc.abstractmethod
    def apply(self, stmt: Select) -> Select:
        raise NotImplementedError(repr(self.apply))


class QueryPageResultBase(
    Base, Generic[ResultType], arbitrary_types_allowed=True, extra="forbid"
):
    data: list[ResultType]

    @classmethod
    def from_orm(cls, obj: Self, t: Type[ResultType]) -> Self:
        return cls(
            **{
                **obj.model_dump(),
                "data": [t.from_orm(o) for o in obj.data],
            }
        )
