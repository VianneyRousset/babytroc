from typing import Self

from pydantic import RootModel, model_validator
from sqlalchemy.dialects.postgresql import Range as SQLRange

from app.schemas.base import Base


class ItemBase(Base):
    pass


class MonthRange(RootModel):
    root: str

    @model_validator(mode="before")
    @classmethod
    def validate_root(cls, range: str | tuple[int | None, int | None] | SQLRange[int]):
        if isinstance(range, tuple):
            return cls.values_as_str(*range)

        if isinstance(range, SQLRange):
            return cls.values_as_str(
                lower=range.lower,
                upper=range.upper,
            )

        return cls.values_as_str(
            lower=cls.extract_lower_from_str(range),
            upper=cls.extract_upper_from_str(range),
        )

    @classmethod
    def from_values(cls, *, lower: int | None, upper: int | None) -> Self:
        return cls(cls.values_as_str(lower, upper))

    @property
    def lower(self) -> int | None:
        return self.extract_lower_from_str(self.model_dump())

    @property
    def upper(self) -> int | None:
        return self.extract_upper_from_str(self.model_dump())

    @property
    def as_tuple(self) -> tuple[int | None, int | None]:
        return (self.lower, self.upper)

    @property
    def as_sql_range(self) -> SQLRange[int]:
        return SQLRange(self.lower, self.upper, bounds="[]")

    @staticmethod
    def extract_lower_from_str(string: str) -> int | None:
        lower, _ = string.split("-")

        if not lower.strip():
            return None

        return int(lower)

    @staticmethod
    def extract_upper_from_str(string: str) -> int | None:
        _, upper = string.split("-")

        if not upper.strip():
            return None

        return int(upper)

    @staticmethod
    def values_as_str(
        lower: int | None,
        upper: int | None,
    ) -> str:
        return f"{'' if lower is None else lower}-{'' if upper is None else upper}"
