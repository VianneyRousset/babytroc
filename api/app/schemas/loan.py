from datetime import datetime
from typing import Optional

from .base import Base
from .chat import MessageRead
from .item import ItemPreviewRead
from .user import UserPreviewRead


class LoanRequestBase(Base):
    pass


class LoanRequestCreate(LoanRequestBase):
    item_id: int


class LoanRequestRead(LoanRequestBase):
    id: int
    item: ItemPreviewRead
    borrower: UserPreviewRead
    message: MessageRead


class LoanBase(Base):
    pass


class LoanRead(LoanBase):
    id: int
    item: ItemPreviewRead
    borrower: UserPreviewRead
    start: datetime
    end: Optional[datetime]
