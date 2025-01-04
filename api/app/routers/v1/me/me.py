from typing import Annotated

from fastapi import Body, Request, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.schemas.user.read import UserRead
from app.schemas.user.update import UserUpdate

from .router import router

# GET


@router.get("", status_code=status.HTTP_200_OK)
def get_client_user(
    request: Request,
    db: Annotated[Session, Depends(get_db_session)],
) -> UserRead:
    """Get client user."""

    client_user_id = services.auth.check_auth(request)

    return services.user.get_user(
        db=db,
        user_id=client_user_id,
    )


# UPDATE


@router.post("", status_code=status.HTTP_200_OK)
def update_client_user(
    request: Request,
    user_update: Annotated[
        UserUpdate,
        Body(title="User fields to update."),
    ],
    db: Annotated[Session, Depends(get_db_session)],
) -> UserRead:
    """Update client user."""

    client_user_id = services.auth.check_auth(request)

    return services.user.update_user(
        db=db,
        user_id=client_user_id,
        user_update=user_update,
    )


# DELETE


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_client_user(
    request: Request,
    db: Annotated[Session, Depends(get_db_session)],
) -> None:
    """Delete client user."""

    client_user_id = services.auth.check_auth(request)

    services.user.delete_user(
        db=db,
        user_id=client_user_id,
    )
