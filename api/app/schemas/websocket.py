from typing import Annotated, Literal

from pydantic import Field

from .base import BaseModel
from .chat.read import ChatMessageRead


class WebSocketBase(BaseModel):
    pass


class WebSocketMessageNewChatMessage(WebSocketBase):
    type: Literal["new_chat_message"]
    message: ChatMessageRead


WebSocketMessage = Annotated[
    WebSocketMessageNewChatMessage, Field(discriminator="type")
]
