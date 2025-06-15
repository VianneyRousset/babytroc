from pydantic import EmailStr, field_validator

from app.schemas.base import CreateBase

from .base import AuthBase


class AuthAccountPasswordResetAuthorizationCreate(AuthBase, CreateBase):
    email: EmailStr

    @field_validator("email", mode="before")
    def validate_email(
        cls,  # noqa: N805
        v: str,
    ) -> str:
        """Remove leading and trailing whitespace and switch to lowercase."""

        if isinstance(v, str):
            return v.strip().lower()
        return v
