import abc
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Select

ResultType = TypeVar("ResultType")


class Base(BaseModel, Generic[ResultType], abc.ABC):
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


class QueryPageBase(Base, extra="forbid"):
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
