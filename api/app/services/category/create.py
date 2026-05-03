from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item.category import Category
from app.schemas.category.create import CategoryCreate
from app.schemas.category.read import CategoryRead


async def create_category(
    db: AsyncSession,
    category_create: CategoryCreate,
) -> CategoryRead:
    """Create a category."""

    categories = await create_many_categories(
        db=db,
        category_creates=[category_create],
    )

    return categories[0]


async def create_many_categories(
    db: AsyncSession,
    category_creates: list[CategoryCreate],
) -> list[CategoryRead]:
    """Create many categories."""

    stmt = (
        insert(Category)
        .values(
            [
                {
                    "slug": cat.slug,
                    "name": cat.name,
                    "parent_slug": cat.parent_slug,
                }
                for cat in category_creates
            ]
        )
        .returning(Category)
    )

    categories = (await db.execute(stmt)).unique().scalars().all()

    return [CategoryRead.model_validate(cat) for cat in categories]
