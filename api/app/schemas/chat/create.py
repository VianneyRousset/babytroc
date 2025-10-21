from typing import Annotated

from pydantic import Field, field_validator

from app.schemas.base import CreateBase

from .base import ChatMessageBase


class ChatMessageCreate(ChatMessageBase, CreateBase):
    text: Annotated[
        str,
        Field(
            min_length=1,
            max_length=1000,
        ),
    ]

    @field_validator("text", mode="before")
    def validate_name(
        cls,  # noqa: N805
        v: str,
    ) -> str:
        """Remove leading and trailing whitespace."""

        if isinstance(v, str):
            return v.strip()
        return v
