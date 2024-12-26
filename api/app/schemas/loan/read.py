from datetime import datetime
from typing import Optional

from app import models
from app.enums import ChatMessageType
from app.schemas.base import ReadBase
from app.schemas.chat.read import ChatMessageRead
from app.schemas.item.preview import ItemPreviewRead
from app.schemas.user.preview import UserPreviewRead

from .base import LoanBase, LoanRequestBase


class LoanRequestRead(LoanRequestBase, ReadBase):
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


class LoanRead(LoanBase, ReadBase):
    id: int
    item: ItemPreviewRead
    borrower: UserPreviewRead
    start: datetime
    end: Optional[datetime]
