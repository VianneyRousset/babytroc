from .base import AuthBase


class TokenData(AuthBase):
    pass


class UserAccessTokenData(TokenData):
    sub: int
