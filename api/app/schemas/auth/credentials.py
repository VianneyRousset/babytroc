from datetime import timedelta

from .base import AuthBase


class Credentials(AuthBase):
    pass


class UserCredentials(Credentials):
    """Tokens for user access."""

    access_token: str
    refresh_token: str
    refresh_token_duration: timedelta
    access_token_duration: timedelta


class UserCredentialsInfo(Credentials):
    """Info about the user credentials.

    Does not contain any token as the latters are given via cookies.
    """

    expires_in: int
