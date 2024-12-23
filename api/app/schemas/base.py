from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

ResultType = TypeVar("ResultType")


class Base(BaseModel, Generic[ResultType]):
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        # extra="forbid",
    )
