from typing import Annotated, Literal

from pydantic import Field, TypeAdapter

from .base import BaseModel
from .chat.read import ChatMessageRead


class WebSocketBase(BaseModel):
    pass


class WebSocketMessageNewChatMessage(WebSocketBase):
    type: Literal["new_chat_message"] = "new_chat_message"
    message: ChatMessageRead


class WebSocketMessageUpdatedChatMessage(WebSocketBase):
    type: Literal["updated_chat_message"] = "updated_chat_message"
    message: ChatMessageRead


WebSocketMessage = WebSocketMessageNewChatMessage | WebSocketMessageUpdatedChatMessage


WebSocketMessageTypeAdapter: TypeAdapter[WebSocketMessage] = TypeAdapter(
    Annotated[WebSocketMessage, Field(discriminator="type")]
)
