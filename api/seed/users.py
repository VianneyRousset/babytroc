import logging
from collections.abc import Iterable

from sqlalchemy.ext.asyncio import AsyncSession
from tqdm import tqdm

import app
from app.domains.user.schemas.create import UserCreate as User

logger = logging.getLogger("seed")


async def check_users(db: AsyncSession) -> bool:
    """Returns True if some users are present in the database."""

    logger.debug("Checking users: started")
    users = await app.services.user.list_users(db)
    logger.debug("%i users found", len(users))
    res = len(users) > 0
    logger.debug("Checking users: done")

    return res


async def populate_users(
    db: AsyncSession,
    users: Iterable[User],
):
    """Populate users."""

    logger.debug("Populating users: started")

    for user in tqdm(users):
        await app.services.user.create_user_without_validation(
            db=db,
            user_create=user,
            validated=True,
        )

    logger.debug("Populating users: done")
