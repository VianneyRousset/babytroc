from .base import AuthBase


class AuthSession(AuthBase):
    logged_in: bool
