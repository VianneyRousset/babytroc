from typing import Annotated, Literal

from pydantic import Field, TypeAdapter

from .base import BaseModel


class PubsubBase(BaseModel):
    pass


class PubsubMessageNewChatMessage(PubsubBase):
    type: Literal["new_chat_message"] = "new_chat_message"
    chat_message_id: int


class PubsubMessageUpdatedChatMessage(PubsubBase):
    type: Literal["updated_chat_message"] = "updated_chat_message"
    chat_message_id: int


PubsubMessage = PubsubMessageNewChatMessage | PubsubMessageUpdatedChatMessage

PubsubMessageTypeAdapter: TypeAdapter[PubsubMessage] = TypeAdapter(
    Annotated[PubsubMessage, Field(discriminator="type")]
)
