import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from babytroc.domains.category import services as category_services
from babytroc.domains.category.schemas.read import CategoryRead
from babytroc.domains.item import services as item_services
from babytroc.domains.item.models.item import Item
from babytroc.domains.item.schemas.read import ItemRead
from babytroc.domains.user.schemas.private import UserPrivateRead
from babytroc.infrastructure.cache_client import NullCache


@pytest.fixture
async def categories(
    database_sessionmaker: async_sessionmaker,
) -> list[CategoryRead]:
    """Fetches the pre-seeded categories."""

    async with database_sessionmaker.begin() as session:
        return await category_services.list_categories(session, NullCache())


@pytest.fixture
async def alice_items_with_categories(
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
) -> list[ItemRead]:
    """SELECT Alice's items with categories from the matching template."""
    async with database_sessionmaker.begin() as session:
        ids = (
            (await session.execute(select(Item.id).where(Item.owner_id == alice.id)))
            .scalars()
            .all()
        )
        if not ids:
            return []
        return await item_services.get_many_items(db=session, item_ids=set(ids))
