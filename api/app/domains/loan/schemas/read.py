from collections.abc import Sequence
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


class LoanRead(LoanBase, ReadBase):
    id: int
    item: ItemPreviewRead
    owner: UserPreviewRead
    borrower: UserPreviewRead
    chat_id: ChatId
    during: tuple[datetime | None, datetime | None]
    loan_request: LoanRequestRead
    active: bool

    @field_validator("during", mode="before")
    def validate_during(
        cls,  # noqa: N805
        v: Sequence[datetime | str | None] | Range,
    ) -> tuple[datetime | None, datetime | None]:
        if isinstance(v, Sequence):
            if len(v) != 2:
                msg = "Range `during` must have exactly two elements"
                raise ValueError(msg)

            lower, upper = v

            return cls._read_datetime(lower), cls._read_datetime(upper)

        return v.lower, v.upper

    @staticmethod
    def _read_datetime(src: datetime | str | None) -> datetime | None:
        if src is None or isinstance(src, datetime):
            return src

        if isinstance(src, str):
            return datetime.fromisoformat(src)

        msg = f"Invalid range bound value type: {type(src)}"
        raise ValueError(msg)
