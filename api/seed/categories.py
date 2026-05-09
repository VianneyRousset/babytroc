import logging
from collections.abc import Iterable

from sqlalchemy.ext.asyncio import AsyncSession
from tqdm import tqdm

from app.domains.category.schemas.create import CategoryCreate as Category
from app.domains.category.services import create_category, list_categories
from app.infrastructure.cache_client import NullCache

logger = logging.getLogger("seed")

_cache = NullCache()


async def check_categories(
    db: AsyncSession,
) -> bool:
    """Returns True if some categories are present in the database."""

    logger.debug("Checking categories: started")
    categories = await list_categories(db, _cache)
    logger.debug("%i categories found", len(categories))
    res = len(categories) > 0
    logger.debug("Checking categories: done")

    return res


async def populate_categories(
    db: AsyncSession,
    categories: Iterable[Category],
) -> None:
    """Populate categories. Parents must come before children."""

    logger.debug("Populating categories: started")

    for category in tqdm(categories):
        await create_category(
            db=db,
            category_create=category,
        )

    logger.debug("Populating categories: done")
