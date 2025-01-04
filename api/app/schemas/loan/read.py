from datetime import datetime
from typing import Union

from pydantic import field_validator
from sqlalchemy.dialects.postgresql import Range

from app.enums import LoanRequestState
from app.schemas.base import ReadBase
from app.schemas.chat.read import ChatMessageRead
from app.schemas.item.preview import ItemPreviewRead
from app.schemas.user.preview import UserPreviewRead

from .base import LoanBase, LoanRequestBase


class LoanRequestRead(LoanRequestBase, ReadBase):
    id: int
    item: ItemPreviewRead
    borrower: UserPreviewRead
    state: LoanRequestState
    creation_chat_message: ChatMessageRead


class LoanRead(LoanBase, ReadBase):
    id: int
    item: ItemPreviewRead
    borrower: UserPreviewRead
    during: tuple[datetime | None, datetime | None]
    active: bool

    @field_validator("during")
    def validate_during(
        cls,  # noqa: N805
        v: Union[tuple[datetime | None, datetime | None], Range],
    ) -> tuple[datetime | None, datetime | None]:
        if isinstance(v, tuple):
            return v

        return v.lower, v.upper
