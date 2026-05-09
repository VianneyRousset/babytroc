from pydantic import EmailStr, field_validator

from app.schemas.base import ApiQueryBase


class AuthAccountAvailabilityApiQuery(ApiQueryBase):
    name: str | None = None
    email: EmailStr | None = None

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
