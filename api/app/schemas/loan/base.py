from collections.abc import Hashable
from typing import Self

from pydantic import RootModel, model_validator

from app.schemas.base import Base


class LoanRequestBase(Base):
    pass


class LoanBase(Base):
    pass


class ItemBorrowerId(RootModel[str], Hashable):
    root: str

    @model_validator(mode="before")
    @classmethod
    def validate_root(cls, value: str):
        return cls.values_as_str(
            item_id=cls.extract_item_id_from_str(value),
            borrower_id=cls.extract_borrower_id_from_str(value),
        )

    @classmethod
    def from_values(cls, *, item_id: int, borrower_id: int) -> Self:
        return cls(
            cls.values_as_str(
                item_id=item_id,
                borrower_id=borrower_id,
            )
        )

    @property
    def item_id(self):
        return self.extract_item_id_from_str(self.model_dump())

    @property
    def borrower_id(self):
        return self.extract_borrower_id_from_str(self.model_dump())

    @staticmethod
    def extract_item_id_from_str(string: str) -> int:
        item_id, _ = string.split("-")
        return int(item_id)

    @staticmethod
    def extract_borrower_id_from_str(string: str) -> int:
        _, borrower_id = string.split("-")
        return int(borrower_id)

    @staticmethod
    def values_as_str(
        *,
        item_id: int,
        borrower_id: int,
    ) -> str:
        return f"{item_id}-{borrower_id}"

    def __str__(self) -> str:
        return self.model_dump()

    def __hash__(self):
        return hash(str(self))

    def __lt__(self, other: Self) -> bool:
        if self.item_id == other.item_id:
            return self.borrower_id < other.borrower_id

        return self.item_id < other.item_id

    def __gt__(self, other: Self) -> bool:
        if self.item_id == other.item_id:
            return self.borrower_id > other.borrower_id

        return self.item_id > other.item_id

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return False

        return self.item_id == other.item_id and self.borrower_id == other.borrower_id
