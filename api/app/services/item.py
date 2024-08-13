from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.item import Item as ItemDB
from app.schemas.item import Item, ItemCreation


async def list_items(session: Session) -> list[Item]:
    return [Item(**item.__dict__) for item in await session.scalars(select(ItemDB))]


def create_item(session: Session, item: ItemCreation) -> Item:
    item = ItemDB(**item.model_dump(exclude_nope=True))
    session.add(item)
    session.commit()
    session.refresh()
    return Item(**item.__dict__)


def get_item(session: Session, item_id: int) -> Item:
    item = session.query(ItemDB).filter(ItemDB.id == item_id).one()
    return Item(**item.__dict__)
