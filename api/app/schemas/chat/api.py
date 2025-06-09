from pydantic import Field

from app.schemas.base import ApiQueryBase


class ChatApiQuery(ApiQueryBase):
    # item_id
    item: int | None = Field(
        title="Item",
        description=("Only select chats about the item with this ID."),
        examples=[42],
        default=None,
    )

    # borrower_id
    borrower: int | None = Field(
        title="Borrower",
        description=("Only select chats with the borrower with this ID."),
        examples=[42],
        default=None,
    )

    # borrower_id
    owner: int | None = Field(
        title="Owner",
        description=("Only select chats with the owner with this ID."),
        examples=[42],
        default=None,
    )

    # limit
    n: int | None = Field(
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
    clm: int | None = Field(
        title="Page cursor for last message ID",
        ge=0,
        default=None,
    )

    # cursor chat_id
    cid: str | None = Field(
        title="Page cursor for item ID",
        pattern=r"\d+-\d+",
        default=None,
    )


class ChatMessageApiQuery(ApiQueryBase):
    # seen
    seen: bool | None = Field(
        title="Seen",
        description=("Only select messages that have been seen."),
        examples=[True, False],
        default=None,
    )

    # limit
    n: int | None = Field(
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
    cid: int | None = Field(
        title="Page cursor for chat message ID",
        ge=0,
        default=None,
    )
