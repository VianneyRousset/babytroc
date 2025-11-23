from app.schemas.base import Base
from app.schemas.loan.base import ItemBorrowerId


class ChatBase(Base):
    pass


class ChatMessageBase(Base):
    pass


class ChatId(ItemBorrowerId):
    pass
