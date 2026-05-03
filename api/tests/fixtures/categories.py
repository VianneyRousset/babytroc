import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from app import services
from app.schemas.category.create import CategoryCreate
from app.schemas.category.read import CategoryRead


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

    children = [
        CategoryCreate(slug="clothing-bodysuits", name="Bodies", parent_slug="clothing"),
        CategoryCreate(slug="clothing-sleepwear", name="Pyjamas", parent_slug="clothing"),
        CategoryCreate(slug="clothing-outerwear", name="Manteaux", parent_slug="clothing"),
        CategoryCreate(slug="clothing-accessories", name="Accessoires", parent_slug="clothing"),
        CategoryCreate(slug="toys-bath", name="Jouets de bain", parent_slug="toys"),
        CategoryCreate(slug="toys-soft", name="Peluches", parent_slug="toys"),
        CategoryCreate(slug="toys-educational", name="Jouets éducatifs", parent_slug="toys"),
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
