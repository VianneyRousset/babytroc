from pydantic import BaseModel
from datetime import datetime
from .users import User, bob
from .items import Item, chair


class LoanRequest(BaseModel):
    item: Item
    borrower: User
    creation_date: datetime


def request_item(item_id: int, borrower_id: int) -> LoanRequest:
    return LoanRequest(
        item=chair,
        borrower=bob,
    )
