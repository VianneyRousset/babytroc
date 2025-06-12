from pydantic import EmailStr

from app.schemas.base import CreateBase

from .base import AuthBase


class AuthAccountPasswordResetAuthorizationCreate(AuthBase, CreateBase):
    email: EmailStr
