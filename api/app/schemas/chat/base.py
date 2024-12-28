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

    def __str__(self):
        return f"{self.item_id}-{self.borrower_id}"
