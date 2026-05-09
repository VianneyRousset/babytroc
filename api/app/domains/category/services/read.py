import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.category.models import Category
from app.domains.category.schemas.read import CategoryRead
from app.infrastructure.cache_client import Cache
from app.infrastructure.cache_keys import TTL_CATEGORIES, key_categories


async def list_categories(
    db: AsyncSession,
    cache: Cache,
) -> list[CategoryRead]:
    """List all categories."""

    cached = await cache.get(key_categories())
    if cached is not None:
        return [CategoryRead.model_validate(c) for c in json.loads(cached)]

    stmt = select(Category).order_by(Category.parent_slug.nulls_first(), Category.slug)

    categories = (await db.execute(stmt)).unique().scalars().all()

    result = [CategoryRead.model_validate(cat) for cat in categories]

    await cache.set(
        key_categories(),
        json.dumps([c.model_dump(mode="json") for c in result]),
        ttl=TTL_CATEGORIES,
    )

    return result
