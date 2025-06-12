from typing import Annotated
from uuid import UUID

from fastapi import BackgroundTasks, Depends, Request
from fastapi_mail import FastMail
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.email import get_email_client
from app.schemas.auth.create import AuthAccountPasswordResetAuthorizationCreate
from app.schemas.auth.reset import (
    AuthAccountPasswordResetAuthorizationCreated,
    AuthAccountPasswordResetDone,
)
from app.schemas.user.update import UserPasswordUpdate

from .router import router


@router.post("/reset-password")
def create_account_password_reset_authorization(
    request: Request,
    db: Annotated[Session, Depends(get_db_session)],
    email_client: Annotated[FastMail, Depends(get_email_client)],
    background_tasks: BackgroundTasks,
    authorization_create: AuthAccountPasswordResetAuthorizationCreate,
) -> AuthAccountPasswordResetAuthorizationCreated:
    """Send a account password reset authorization by email."""

    services.auth.create_account_password_reset_authrorization(
        db=db,
        user_email=authorization_create.email,
        email_client=email_client,
        background_tasks=background_tasks,
        app_name=request.app.state.config.app_name,
    )

    return AuthAccountPasswordResetAuthorizationCreated()


@router.post("/reset-password/{authorization_code}")
def validate_user_account(
    request: Request,
    db: Annotated[Session, Depends(get_db_session)],
    email_client: Annotated[FastMail, Depends(get_email_client)],
    background_tasks: BackgroundTasks,
    authorization_code: UUID,
    user_password_update: UserPasswordUpdate,
) -> AuthAccountPasswordResetDone:
    """Apply the account password reset with `authorization_code`."""

    services.auth.apply_account_password_reset(
        db=db,
        authorization_code=authorization_code,
        new_password=user_password_update.password,
        email_client=email_client,
        background_tasks=background_tasks,
        app_name=request.app.state.config.app_name,
        config=request.app.state.config.auth,
    )

    return AuthAccountPasswordResetDone()
