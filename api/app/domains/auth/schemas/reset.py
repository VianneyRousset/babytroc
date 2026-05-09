from typing import Literal

from .base import AuthBase


class AuthAccountPasswordResetAuthorizationCreated(AuthBase):
    result: Literal["ok"] = "ok"


class AuthAccountPasswordResetDone(AuthBase):
    result: Literal["ok"] = "ok"
