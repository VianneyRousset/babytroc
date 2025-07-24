import re
from typing import Annotated

from pydantic import EmailStr, Field, field_validator

from app.schemas.base import CreateBase
from app.utils.hash import HashedStr

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
    password: str | HashedStr
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
        v: str | HashedStr,
    ) -> HashedStr:
        """Check containing lower and upper case characters."""

        # skip checks if hashed
        if isinstance(v, HashedStr):
            return v

        # check length and mandatory characters
        if isinstance(v, str):
            if v.lower() == v or v.upper() == v:
                msg = "The password must contain lowercase and uppercase letters."
                raise ValueError(msg)
            if not re.match(r".*[0-9].*", v):
                msg = "The password must contain at least one digit."
                raise ValueError(msg)
            if len(v) < PASSWORD_MIN_LENGTH:
                msg = (
                    f"The password must contain at least {PASSWORD_MIN_LENGTH} "
                    "characters."
                )
                raise ValueError(msg)

        return HashedStr(v)

    @field_validator("avatar_seed", mode="before")
    def validate_avatar_seed(
        cls,  # noqa: N805
        v: str,
    ) -> str:
        """Remove leading and trailing whitespace and switch to lowercase."""

        if isinstance(v, str):
            return v.strip().lower()
        return v
