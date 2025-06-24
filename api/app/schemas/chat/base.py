from typing import Self

from pydantic import RootModel, model_validator

from app.schemas.base import Base


class ChatBase(Base):
    pass


class ChatMessageBase(Base):
    pass


class ChatId(RootModel):
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
