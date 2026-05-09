from typing import Annotated

from pydantic import Field, field_validator

from app.schemas.base import UpdateBase

from .base import UserBase
from .constants import AVATAR_SEED_LENGTH, NAME_LENGTH, PASSWORD_MIN_LENGTH


class UserUpdate(UserBase, UpdateBase):
    name: Annotated[
        str | None,
        Field(
            min_length=NAME_LENGTH.start,
            max_length=NAME_LENGTH.stop,
        ),
    ] = None
    avatar_seed: Annotated[
        str | None,
        Field(
            min_length=AVATAR_SEED_LENGTH.start,
            max_length=AVATAR_SEED_LENGTH.stop,
        ),
    ] = None


class UserPasswordUpdate(UserBase, UpdateBase):
    password: Annotated[
        str,
        Field(
            pattern="[0-9]",
            min_length=PASSWORD_MIN_LENGTH,
        ),
    ]

    @field_validator("password", mode="before")
    def validate_password(
        cls,  # noqa: N805
        v: str,
    ) -> str:
        """Check containing lower and upper case characters."""

        if isinstance(v, str):
            if v.lower() == v or v.upper() == v:
                msg = "The password must contain lowercase and uppercase letters."
                raise ValueError(msg)

        return v
