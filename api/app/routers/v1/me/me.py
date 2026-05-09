from typing import Annotated

from fastapi import Body, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.user import services as user_services
from app.infrastructure.cache import get_cache
from app.infrastructure.cache_client import Cache
from app.infrastructure.database import get_db_session
from app.routers.v1.auth import client_id_annotation
from app.domains.user.schemas.private import UserPrivateRead
from app.domains.user.schemas.update import UserUpdate

from .router import router

# GET


@router.get("", status_code=status.HTTP_200_OK)
async def get_client_user(
    client_id: client_id_annotation,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserPrivateRead:
    """Get client user."""

    return await user_services.get_user_private(
        db=db,
        user_id=client_id,
    )


# UPDATE


@router.post("", status_code=status.HTTP_200_OK)
async def update_client_user(
    client_id: client_id_annotation,
    request: Request,
    user_update: Annotated[
        UserUpdate,
        Body(title="User fields to update."),
    ],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    cache: Annotated[Cache, Depends(get_cache)],
) -> UserPrivateRead:
    """Update client user."""

    return await user_services.update_user(
        db=db,
        user_id=client_id,
        user_update=user_update,
        cache=cache,
    )


# DELETE


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client_user(
    client_id: client_id_annotation,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    cache: Annotated[Cache, Depends(get_cache)],
) -> None:
    """Delete client user."""

    await user_services.delete_user(
        db=db,
        user_id=client_id,
        cache=cache,
    )
