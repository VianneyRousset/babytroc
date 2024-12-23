from datetime import datetime
from typing import TYPE_CHECKING, Optional

from app.schemas.item.preview import ItemPreviewRead
from app.schemas.user.preview import UserPreviewRead
from app.enums import ChatMessageType
from app import models

from .base import Base
from .chat import ChatMessageRead


class LoanRequestBase(Base):
    pass


class LoanRequestCreate(LoanRequestBase):
    item_id: int


class LoanRequestRead(LoanRequestBase):
    id: int
    item: ItemPreviewRead
    borrower: UserPreviewRead
    message: ChatMessageRead

    @classmethod
    def from_orm(
        cls,
        *,
        loan_request: models.loan.LoanRequest,
        message: models.chat.ChatMessage,
    ):
        return cls(
            id=loan_request.id,
            item=ItemPreviewRead.from_orm(loan_request.item),
            borrower=UserPreviewRead.from_orm(loan_request.borrower),
            message=ChatMessageRead(
                id=1,
                message_type=ChatMessageType.loan_start,
                sender_id=1,
                receiver_id=1,
                creation_date=datetime.now(),
                seen=False,
                payload="salut",
            ),
        )


class LoanBase(Base):
    pass


class LoanRead(LoanBase):
    id: int
    item: ItemPreviewRead
    borrower: UserPreviewRead
    start: datetime
    end: Optional[datetime]
