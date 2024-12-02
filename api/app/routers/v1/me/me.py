from typing import Annotated

from fastapi import APIRouter, Body, Request, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app import database as db
from app import services
from app.schemas.users import UserRead, UserUpdate

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK)
async def get_client_user(
    request: Request,
    db: Session = Depends(db.get_session),
) -> UserRead:
    """Get client user."""

    client_user_id = services.auth.check_auth(request)

    return await services.users.get_user_by_id(
        db=db,
        user_id=client_user_id,
    )


@router.post("", status_code=status.HTTP_200_OK)
async def update_client_user(
    request: Request,
    user_update: Annotated[
        UserUpdate,
        Body(title="User fields to update."),
    ],
    db: Session = Depends(db.get_session),
) -> UserRead:
    """Update client user."""

    client_user_id = services.auth.check_auth(request)

    return await services.users.update_user(
        db=db,
        user_id=client_user_id,
        user_update=user_update,
    )


@router.delete("", status_code=status.HTTP_200_OK)
async def delete_client_user(
    request: Request,
    db: Session = Depends(db.get_session),
) -> UserRead:
    """Delete client user."""

    client_user_id = services.auth.check_auth(request)

    await services.users.delete_user(
        db=db,
        user_id=client_user_id,
    )
