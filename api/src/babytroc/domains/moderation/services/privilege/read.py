import json
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.moderation.schemas.read import ModerationPrivilegeRead
from babytroc.domains.user.models import User
from babytroc.infrastructure.cache_keys import (
    TTL_MODERATION_PRIVILEGE,
    key_moderation_privilege_admins,
    key_moderation_privilege_moderators,
)

if TYPE_CHECKING:
    from babytroc.infrastructure.cache_client import Cache


async def get_all_moderators(
    db: AsyncSession,
    *,
    cache: "Cache | None" = None,
) -> list[ModerationPrivilegeRead]:
    """Get the email of all moderators."""

    # use cache
    if cache is not None:
        cached = await cache.get(key_moderation_privilege_moderators())
        if cached is not None:
            return [
                ModerationPrivilegeRead.model_validate(moderator)
                for moderator in json.loads(cached)
            ]

    stmt = select(User).where(User.moderator.is_(True)).order_by(User.id)

    # execute
    res = await db.execute(stmt)
    moderators = [
        ModerationPrivilegeRead(
            user_id=user.id,
            name=user.name,
            email=user.email,
            admin=user.admin,
            moderator=user.moderator,
        )
        for user in res.unique().all()
    ]

    # update cache
    if cache is not None:
        await cache.set(
            key_moderation_privilege_moderators(),
            json.dumps([moderator.model_dump(mode="json") for moderator in moderators]),
            ttl=TTL_MODERATION_PRIVILEGE,
        )

    return moderators


async def get_all_admins(
    db: AsyncSession,
    *,
    cache: "Cache | None" = None,
) -> list[ModerationPrivilegeRead]:
    """Get the email of all admins."""

    # use cache
    if cache is not None:
        cached = await cache.get(key_moderation_privilege_admins())
        if cached is not None:
            return [
                ModerationPrivilegeRead.model_validate(admin)
                for admin in json.loads(cached)
            ]

    stmt = select(User).where(User.admin.is_(True)).order_by(User.id)

    # execute
    res = await db.execute(stmt)
    admins = [
        ModerationPrivilegeRead(
            user_id=user.id,
            name=user.name,
            email=user.email,
            admin=user.admin,
            moderator=user.moderator,
        )
        for user in res.unique().all()
    ]

    # update cache
    if cache is not None:
        await cache.set(
            key_moderation_privilege_admins(),
            json.dumps([admin.model_dump(mode="json") for admin in admins]),
            ttl=TTL_MODERATION_PRIVILEGE,
        )

    return admins
