from typing import Annotated, Literal

from pydantic import Field, TypeAdapter

from .base import BaseModel
from .chat.read import ChatMessageRead


class WebSocketMessageBase(BaseModel):
    pass


class WebSocketMessageNewChatMessage(WebSocketMessageBase):
    type: Literal["new_chat_message"] = "new_chat_message"
    message: ChatMessageRead


class WebSocketMessageUpdatedChatMessage(WebSocketMessageBase):
    type: Literal["updated_chat_message"] = "updated_chat_message"
    message: ChatMessageRead


class WebsocketMessageUpdatedAccountValidation(WebSocketMessageBase):
    type: Literal["updated_account_validation"] = "updated_account_validation"
    validated: bool


WebSocketMessage = (
    WebSocketMessageNewChatMessage
    | WebSocketMessageUpdatedChatMessage
    | WebsocketMessageUpdatedAccountValidation
)


WebSocketMessageTypeAdapter: TypeAdapter[WebSocketMessage] = TypeAdapter(
    Annotated[WebSocketMessage, Field(discriminator="type")]
)
