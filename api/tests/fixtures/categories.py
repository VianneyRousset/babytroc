import random

import pytest
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import async_sessionmaker

from babytroc.domains.category import services as category_services
from babytroc.domains.category.schemas.read import CategoryRead
from babytroc.domains.item.models.category import ItemCategoryAssociation
from babytroc.domains.item.schemas.read import ItemRead
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
    alice_many_items: list[ItemRead],
    categories: list[CategoryRead],
) -> list[ItemRead]:
    """Assign 1-3 random categories to each of alice's many items."""

    random.seed(0xCAFE)

    child_categories = [cat for cat in categories if cat.parent_slug is not None]
    associations = []

    for item in alice_many_items:
        chosen = random.sample(
            child_categories,
            k=random.randint(1, min(3, len(child_categories))),
        )
        for cat in chosen:
            associations.append(
                {"item_id": item.id, "category_slug": cat.slug}
            )

    async with database_sessionmaker.begin() as session:
        await session.execute(
            insert(ItemCategoryAssociation).values(associations)
        )

    # Re-read items to get updated category_slugs
    from babytroc.domains.item.services import get_many_items

    async with database_sessionmaker() as session:
        items = await get_many_items(
            db=session,
            item_ids={item.id for item in alice_many_items},
        )

    return items
