from typing import Annotated, Literal

from pydantic import Field, TypeAdapter

from app.enums import ChatMessageType
from app.schemas.base import BaseModel

from .base import ChatId


class SendChatMessageBase(BaseModel):
    type: ChatMessageType
    chat_id: ChatId
    sender_id: int | None = None
    text: str | None = None
    loan_request_id: int | None = None
    loan_id: int | None = None


class SendChatMessageText(SendChatMessageBase):
    type: Literal[ChatMessageType.text] = ChatMessageType.text
    sender_id: int
    text: str


class SendChatMessageLoanRequestCreated(SendChatMessageBase):
    type: Literal[ChatMessageType.loan_request_created] = (
        ChatMessageType.loan_request_created
    )
    loan_request_id: int


class SendChatMessageLoanRequestCancelled(SendChatMessageBase):
    type: Literal[ChatMessageType.loan_request_cancelled] = (
        ChatMessageType.loan_request_cancelled
    )
    loan_request_id: int


class SendChatMessageLoanRequestAccepted(SendChatMessageBase):
    type: Literal[ChatMessageType.loan_request_accepted] = (
        ChatMessageType.loan_request_accepted
    )
    loan_request_id: int


class SendChatMessageLoanRequestRejected(SendChatMessageBase):
    type: Literal[ChatMessageType.loan_request_rejected] = (
        ChatMessageType.loan_request_rejected
    )
    loan_request_id: int


class SendChatMessageLoanStarted(SendChatMessageBase):
    type: Literal[ChatMessageType.loan_started] = ChatMessageType.loan_started
    loan_id: int


class SendChatMessageLoanEnded(SendChatMessageBase):
    type: Literal[ChatMessageType.loan_ended] = ChatMessageType.loan_ended
    loan_id: int


class SendChatMessageItemNotAvailable(SendChatMessageBase):
    type: Literal[ChatMessageType.item_not_available] = (
        ChatMessageType.item_not_available
    )


class SendChatMessageItemAvailable(SendChatMessageBase):
    type: Literal[ChatMessageType.item_available] = ChatMessageType.item_available


SendChatMessage = (
    SendChatMessageText
    | SendChatMessageLoanRequestCreated
    | SendChatMessageLoanRequestCancelled
    | SendChatMessageLoanRequestAccepted
    | SendChatMessageLoanRequestRejected
    | SendChatMessageLoanStarted
    | SendChatMessageLoanEnded
    | SendChatMessageItemNotAvailable
    | SendChatMessageItemAvailable
)

SendChatMessageTypeAdapter: TypeAdapter[SendChatMessage] = TypeAdapter(
    Annotated[SendChatMessage, Field(discriminator="type")]
)
