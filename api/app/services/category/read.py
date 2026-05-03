from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item import Category
from app.schemas.category.read import CategoryRead


async def list_categories(
    db: AsyncSession,
) -> list[CategoryRead]:
    """List all categories."""

    stmt = select(Category).order_by(Category.parent_slug.nulls_first(), Category.slug)

    categories = (await db.execute(stmt)).unique().scalars().all()

    return [CategoryRead.model_validate(cat) for cat in categories]
