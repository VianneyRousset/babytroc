from app.schemas.base import CreateBase

from .base import LoanRequestBase


class LoanRequestCreate(LoanRequestBase, CreateBase):
    item_id: int
