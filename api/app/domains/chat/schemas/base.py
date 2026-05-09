from app.shared.schemas import Base
from app.domains.loan.schemas.base import ItemBorrowerId


class ChatBase(Base):
    pass


class ChatMessageBase(Base):
    pass


class ChatId(ItemBorrowerId):
    pass
