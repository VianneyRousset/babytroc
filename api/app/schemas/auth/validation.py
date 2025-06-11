from typing import Literal

from .base import AuthBase


class AuthValidation(AuthBase):
    result: Literal["ok"]
