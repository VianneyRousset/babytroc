"""Reference + per-item-attachment category seeds."""

import random

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.category.schemas.create import CategoryCreate
from babytroc.domains.category.services import create_many_categories, list_categories
from babytroc.domains.item.models.category import ItemCategoryAssociation
from babytroc.domains.item.models.item import Item
from babytroc.domains.user.services import get_user_by_email_private
from babytroc.infrastructure.cache_client import NullCache
from tests.fixtures.database.infrastructure.chain import SeedContext

_PARENTS = [
    CategoryCreate(slug="clothing", name="Vêtements"),
    CategoryCreate(slug="toys", name="Jouets"),
    CategoryCreate(slug="gear", name="Équipement"),
]

_CHILDREN = [
    CategoryCreate(slug="clothing-bodysuits", name="Bodies", parent_slug="clothing"),
    CategoryCreate(slug="clothing-sleepwear", name="Pyjamas", parent_slug="clothing"),
    CategoryCreate(slug="clothing-outerwear", name="Manteaux", parent_slug="clothing"),
    CategoryCreate(
        slug="clothing-accessories",
        name="Accessoires",
        parent_slug="clothing",
    ),
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


async def seed_reference_categories(db: AsyncSession, ctx: SeedContext) -> None:
    """Insert the canonical 3 parent + 10 child categories."""
    del ctx
    await create_many_categories(db=db, category_creates=_PARENTS)
    await create_many_categories(db=db, category_creates=_CHILDREN)


async def seed_alice_items_with_categories(
    db: AsyncSession,
    ctx: SeedContext,
) -> None:
    """Assign 1-3 random categories to each of Alice's items. Seed: 0xCAFE."""
    del ctx
    random.seed(0xCAFE)

    alice = await get_user_by_email_private(db=db, email="alice@babytroc.ch")
    categories = await list_categories(db, NullCache())
    child_categories = [c for c in categories if c.parent_slug is not None]

    item_ids = (
        (await db.execute(select(Item.id).where(Item.owner_id == alice.id)))
        .scalars()
        .all()
    )

    associations: list[dict[str, object]] = []
    for item_id in item_ids:
        chosen = random.sample(
            child_categories,
            k=random.randint(1, min(3, len(child_categories))),
        )
        associations.extend(
            {"item_id": item_id, "category_slug": cat.slug} for cat in chosen
        )

    if associations:
        await db.execute(insert(ItemCategoryAssociation).values(associations))
