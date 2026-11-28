import json
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.moderation.schemas.read import ModeratorRead
from babytroc.domains.user.models import User
from babytroc.infrastructure.cache_keys import (
    TTL_MODERATION_MODERATORS,
    key_moderation_all_moderators,
)

if TYPE_CHECKING:
    from babytroc.infrastructure.cache_client import Cache


async def get_all_moderators(
    db: AsyncSession,
    *,
    cache: "Cache | None" = None,
) -> list[ModeratorRead]:
    """Get the email of all moderators."""

    # use cache
    if cache is not None:
        cached = await cache.get(key_moderation_all_moderators())
        if cached is not None:
            return [
                ModeratorRead.model_validate(moderator)
                for moderator in json.loads(cached)
            ]

    stmt = select(User).where(User.moderator.is_(True)).order_by(User.id)

    # execute
    res = await db.execute(stmt)
    moderators = [
        ModeratorRead(
            user_id=user.id,
            name=user.name,
            email=user.email,
            admin=user.admin,
        )
        for user in res.unique().all()
    ]

    # update cache
    if cache is not None:
        await cache.set(
            key_moderation_all_moderators(),
            json.dumps([moderator.model_dump(mode="json") for moderator in moderators]),
            ttl=TTL_MODERATION_MODERATORS,
        )

    return moderators
