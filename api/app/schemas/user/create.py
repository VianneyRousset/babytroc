from typing import Annotated

from pydantic import EmailStr, Field, field_validator

from app.schemas.base import CreateBase

from .base import UserBase
from .constants import AVATAR_SEED_LENGTH, NAME_LENGTH, PASSWORD_MIN_LENGTH


class UserCreate(UserBase, CreateBase):
    name: Annotated[
        str,
        Field(
            pattern=r"^\p{L}[\p{L} -]+\p{L}$",
            min_length=NAME_LENGTH.start,
            max_length=NAME_LENGTH.stop,
        ),
    ]
    email: EmailStr
    password: Annotated[
        str,
        Field(
            pattern="[0-9]",
            min_length=PASSWORD_MIN_LENGTH,
        ),
    ]
    avatar_seed: Annotated[
        str | None,
        Field(
            pattern="^[0-9a-f]+$",
            min_length=AVATAR_SEED_LENGTH.start,
            max_length=AVATAR_SEED_LENGTH.stop,
        ),
    ] = None

    @field_validator("name", mode="before")
    def validate_name(
        cls,  # noqa: N805
        v: str,
    ) -> str:
        """Remove leading and trailing whitespace."""

        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("email", mode="before")
    def validate_email(
        cls,  # noqa: N805
        v: str,
    ) -> str:
        """Remove leading and trailing whitespace and switch to lowercase."""

        if isinstance(v, str):
            return v.strip().lower()
        return v

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

    @field_validator("avatar_seed", mode="before")
    def validate_avatar_seed(
        cls,  # noqa: N805
        v: str,
    ) -> str:
        """Remove leading and trailing whitespace and switch to lowercase."""

        if isinstance(v, str):
            return v.strip().lower()
        return v
