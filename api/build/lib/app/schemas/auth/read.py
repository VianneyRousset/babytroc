from datetime import datetime

from app.schemas.base import ReadBase

from .base import AuthBase


class AuthRefreshTokenRead(AuthBase, ReadBase):
    token: str
    user_id: int
    creation_date: datetime
