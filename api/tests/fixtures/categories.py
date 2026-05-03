import random

import pytest
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import async_sessionmaker

from app import services
from app.models.item.category import ItemCategoryAssociation
from app.schemas.category.create import CategoryCreate
from app.schemas.category.read import CategoryRead
from app.schemas.item.read import ItemRead


@pytest.fixture(scope="class")
async def categories(
    database_sessionmaker: async_sessionmaker,
) -> list[CategoryRead]:
    """Ensures categories exist."""

    parents = [
        CategoryCreate(slug="clothing", name="Vêtements"),
        CategoryCreate(slug="toys", name="Jouets"),
        CategoryCreate(slug="gear", name="Équipement"),
    ]

    c = "clothing"
    children = [
        CategoryCreate(slug="clothing-bodysuits", name="Bodies", parent_slug=c),
        CategoryCreate(slug="clothing-sleepwear", name="Pyjamas", parent_slug=c),
        CategoryCreate(slug="clothing-outerwear", name="Manteaux", parent_slug=c),
        CategoryCreate(slug="clothing-accessories", name="Accessoires", parent_slug=c),
        CategoryCreate(slug="toys-bath", name="Jouets de bain", parent_slug="toys"),
        CategoryCreate(slug="toys-soft", name="Peluches", parent_slug="toys"),
        CategoryCreate(
            slug="toys-educational",
            name="Jouets éducatifs",
            parent_slug="toys",
        ),
        CategoryCreate(slug="gear-strollers", name="Poussettes", parent_slug="gear"),
        CategoryCreate(slug="gear-car-seats", name="Sièges auto", parent_slug="gear"),
        CategoryCreate(slug="gear-carriers", name="Porte-bébés", parent_slug="gear"),
    ]

    async with database_sessionmaker.begin() as session:
        created_parents = await services.category.create_many_categories(
            session,
            category_creates=parents,
        )

        created_children = await services.category.create_many_categories(
            session,
            category_creates=children,
        )

    return created_parents + created_children


@pytest.fixture(scope="class")
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
    from app.services.item import get_many_items

    async with database_sessionmaker() as session:
        items = await get_many_items(
            db=session,
            item_ids={item.id for item in alice_many_items},
        )

    return items
