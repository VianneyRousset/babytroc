from pydantic import EmailStr

from app.schemas.base import ApiQueryBase


class AuthAccountAvailabilityApiQuery(ApiQueryBase):
    name: str | None = None
    email: EmailStr | None = None
