"""Reference category seed."""

from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.category.schemas.create import CategoryCreate
from babytroc.domains.category.services import create_many_categories
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
