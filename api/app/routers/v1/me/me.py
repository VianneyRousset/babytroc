from typing import Annotated

from fastapi import Body, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import services
from app.database import get_db_async_session
from app.routers.v1.auth import client_id_annotation
from app.schemas.user.private import UserPrivateRead
from app.schemas.user.update import UserUpdate

from .router import router

# GET


@router.get("", status_code=status.HTTP_200_OK)
async def get_client_user(
    client_id: client_id_annotation,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_async_session)],
) -> UserPrivateRead:
    """Get client user."""

    return await services.user.get_user_private(
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
    db: Annotated[AsyncSession, Depends(get_db_async_session)],
) -> UserPrivateRead:
    """Update client user."""

    return await services.user.update_user(
        db=db,
        user_id=client_id,
        user_update=user_update,
    )


# DELETE


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client_user(
    client_id: client_id_annotation,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_async_session)],
) -> None:
    """Delete client user."""

    await services.user.delete_user(
        db=db,
        user_id=client_id,
    )
