from datetime import datetime

from pydantic import field_validator
from sqlalchemy.dialects.postgresql import Range

from app.enums import LoanRequestState
from app.schemas.base import ReadBase
from app.schemas.chat.base import ChatId
from app.schemas.item.preview import ItemPreviewRead
from app.schemas.user.preview import UserPreviewRead

from .base import LoanBase, LoanRequestBase


class LoanRequestRead(LoanRequestBase, ReadBase):
    id: int
    item: ItemPreviewRead
    borrower: UserPreviewRead
    chat_id: ChatId
    state: LoanRequestState

    @field_validator("chat_id", mode="before")
    def validate_chat_id(
        cls,  # noqa: N805
        v: ChatId | str,
    ) -> ChatId:
        if isinstance(v, str):
            return ChatId.from_str(v)
        return v


class LoanRead(LoanBase, ReadBase):
    id: int
    item: ItemPreviewRead
    owner: UserPreviewRead
    borrower: UserPreviewRead
    chat_id: ChatId
    during: tuple[datetime | None, datetime | None]
    active: bool

    @field_validator("during", mode="before")
    def validate_during(
        cls,  # noqa: N805
        v: tuple[datetime | None, datetime | None] | Range,
    ) -> tuple[datetime | None, datetime | None]:
        if isinstance(v, tuple):
            return v

        return v.lower, v.upper

    @field_validator("chat_id", mode="before")
    def validate_chat_id(
        cls,  # noqa: N805
        v: ChatId | str,
    ) -> ChatId:
        if isinstance(v, str):
            return ChatId.from_str(v)
        return v
