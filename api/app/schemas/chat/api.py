from typing import Optional

from pydantic import Field

from app.schemas.base import ApiQueryBase


class ChatApiQuery(ApiQueryBase):
    # item_id
    item: Optional[int] = Field(
        title="Item",
        description=("Only select chats about the item with this ID."),
        examples=[42],
        default=None,
    )

    # borrower_id
    borrower: Optional[int] = Field(
        title="Borrower",
        description=("Only select chats with the borrower with this ID."),
        examples=[42],
        default=None,
    )

    # borrower_id
    owner: Optional[int] = Field(
        title="Owner",
        description=("Only select chats with the owner with this ID."),
        examples=[42],
        default=None,
    )

    # limit
    n: Optional[int] = Field(
        title="Limit returned chats count",
        description="Limit the number of chats returned.",
        examples=[
            [42],
        ],
        gt=0,
        le=128,
        default=64,
    )

    # cursor last_message_id
    clm: Optional[int] = Field(
        title="Page cursor for last message ID",
        ge=0,
        default=None,
    )

    # cursor chat_id
    cid: Optional[str] = Field(
        title="Page cursor for item ID",
        pattern=r"\d+-\d+",
        default=None,
    )


class ChatMessageApiQuery(ApiQueryBase):
    # seen
    seen: Optional[bool] = Field(
        title="Seen",
        description=("Only select messages that have been seen."),
        examples=[True, False],
        default=None,
    )

    # limit
    n: Optional[int] = Field(
        title="Limit returned messages count",
        description="Limit the number of messages returned.",
        examples=[
            [42],
        ],
        gt=0,
        le=128,
        default=64,
    )

    # cursor message_id
    cid: Optional[int] = Field(
        title="Page cursor for chat message ID",
        ge=0,
        default=None,
    )
