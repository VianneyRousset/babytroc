from datetime import datetime

from .base import Base
from .item import Item
from .user import User


class LoanRequest(Base):
    item: Item
    borrower: User
    creation_date: datetime


class LoanRequestCreation(Base):
    item_id: int
    borrower_id: int
    creation_date: datetime
