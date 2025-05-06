from typing import Annotated, Literal

from pydantic import Field

from .base import BaseModel


class PubsubBase(BaseModel):
    pass


class PubsubMessageNewChatMessage(PubsubBase):
    type: Literal["new_chat_message"]
    chat_message_id: int


PubsubMessage = Annotated[PubsubMessageNewChatMessage, Field(discriminator="type")]
