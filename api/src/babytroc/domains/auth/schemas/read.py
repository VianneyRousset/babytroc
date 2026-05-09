from datetime import datetime

from babytroc.shared.schemas import ReadBase

from .base import AuthBase


class AuthRefreshTokenRead(AuthBase, ReadBase):
    token: str
    user_id: int
    creation_date: datetime
