from app.domains.loan.schemas.base import ItemBorrowerId
from app.shared.schemas import Base


class ChatBase(Base):
    pass


class ChatMessageBase(Base):
    pass


class ChatId(ItemBorrowerId):
    pass
