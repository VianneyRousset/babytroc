from datetime import datetime
from typing import TYPE_CHECKING, Optional

from .base import Base
from .chat import ChatMessageRead

if TYPE_CHECKING:
    from .item import ItemPreviewRead
    from .user import UserPreviewRead


class LoanRequestBase(Base):
    pass


class LoanRequestCreate(LoanRequestBase):
    item_id: int


class LoanRequestRead(LoanRequestBase):
    id: int
    item: "ItemPreviewRead"
    borrower: "UserPreviewRead"
    message: ChatMessageRead


class LoanBase(Base):
    pass


class LoanRead(LoanBase):
    id: int
    item: "ItemPreviewRead"
    borrower: "UserPreviewRead"
    start: datetime
    end: Optional[datetime]
