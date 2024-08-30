from datetime import datetime
from typing import Optional

from .base import Base
from .user import User


class Item(Base):
    id: int
    creation_date: datetime
    # owner: User
    name: str
    description: Optional[str] = None
    # image: str
    # is_available: bool


class PrivateItem(Item):
    request_count: int


class ItemCreation(Base):
    id: int
    owner_id: int
    name: str
    description: Optional[str] = None
    image: str


class ItemUpdate(Base):
    name: Optional[str] = None
    description: Optional[str] = None
