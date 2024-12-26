import abc
from typing import Generic, Self, TypeVar

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


class QueryFilterBase(Base):
    @abc.abstractmethod
    def apply(self, stmt: Select) -> Select:
        raise NotImplementedError(repr(self.apply))


class QueryPageOptionsBase(Base):
    pass


class QueryPageResultBase(Base, Generic[ResultType], arbitrary_types_allowed=True):
    data: list[ResultType]

    def from_orm(self, obj: Self) -> Self:
        return type(self)(
            **{
                **obj.model_dump(),
                "data": [ResultType.from_orm(o) for o in obj.data],
            }
        )
