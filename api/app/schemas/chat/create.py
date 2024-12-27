from app.schemas.base import CreateBase

from .base import ChatMessageBase


class ChatMessageCreate(ChatMessageBase, CreateBase):
    payload: str
