from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from .users import User, alice


class Item(BaseModel):
    id: int
    creation_date: datetime
    owner: User
    name: str
    description: Optional[str] = None
    image: str
    is_available: bool


class PrivateItem(Item):
    request_count: int


class ItemCreation(BaseModel):
    id: int
    owner_id: int
    name: str
    description: Optional[str] = None
    image: str


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


chair = Item(
    id=0,
    creation_date=datetime.now(),
    owner=alice,
    name="Chair",
    description="A nice looking furniture.",
    image="weoijrf",
    is_available=True,
)

door = Item(
    id=1,
    creation_date=datetime.now(),
    owner=alice,
    name="Door",
    description=None,
    image="triuher",
    is_available=False,
)


def list_items() -> list[Item]:
    return [chair, door]


def create_item(item: ItemCreation) -> Item:
    pass


def get_item(item_id: int) -> Item:
    return {0: chair, 1: door}[item_id]
