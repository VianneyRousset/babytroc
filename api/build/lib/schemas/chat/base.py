from pydantic import model_serializer

from app.schemas.base import Base


class ChatBase(Base):
    pass


class ChatMessageBase(Base):
    pass


class ChatId(Base):
    item_id: int
    borrower_id: int

    @classmethod
    def from_str(cls, v: str):
        item_id, borrower_id = v.split("-")

        return cls(
            item_id=int(item_id),
            borrower_id=int(borrower_id),
        )

    @model_serializer
    def ser_model(self) -> str:
        return str(self)

    def __str__(self):
        return f"{self.item_id}-{self.borrower_id}"
