from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.moderation import services as moderation_services
from babytroc.domains.moderation.schemas.read import ModerationPrivilegeRead
from babytroc.infrastructure.cache import get_cache
from babytroc.infrastructure.cache_client import Cache
from babytroc.infrastructure.database import get_db_session
from babytroc.routers.v1.auth.annotations import client_id_annotation_admin
from babytroc.routers.v1.users.annotations import user_id_annotation

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def list_all_admins(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    client_id: client_id_annotation_admin,
    cache: Annotated[Cache, Depends(get_cache)],
) -> list[ModerationPrivilegeRead]:
    """List all admins."""

    return await moderation_services.get_all_admins(db, cache=cache)


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_admin(
    user_id: user_id_annotation,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    client_id: client_id_annotation_admin,
) -> ModerationPrivilegeRead:
    """Get admin."""

    return await moderation_services.get_admin(db, user_id)


@router.post("/{user_id}", status_code=status.HTTP_201_CREATED)
async def create_admin(
    user_id: user_id_annotation,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    cache: Annotated[Cache, Depends(get_cache)],
    client_id: client_id_annotation_admin,
) -> ModerationPrivilegeRead:
    """Add admin privilege to user."""

    return await moderation_services.create_admin(
        db=db,
        user_id=user_id,
        cache=cache,
    )


@router.post("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_admin(
    user_id: user_id_annotation,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    cache: Annotated[Cache, Depends(get_cache)],
    client_id: client_id_annotation_admin,
) -> None:
    """Remove admin privilege to user."""

    return await moderation_services.delete_admin(
        db=db,
        user_id=user_id,
        cache=cache,
    )
