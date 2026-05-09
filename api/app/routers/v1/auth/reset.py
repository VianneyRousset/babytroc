from typing import Annotated
from uuid import UUID

from fastapi import BackgroundTasks, Depends, Request
from fastapi_mail import FastMail
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.auth import services as auth_services
from app.infrastructure.database import get_db_session
from app.infrastructure.email import get_email_client
from app.domains.auth.schemas.create import AuthAccountPasswordResetAuthorizationCreate
from app.domains.auth.schemas.reset import (
    AuthAccountPasswordResetAuthorizationCreated,
    AuthAccountPasswordResetDone,
)
from app.domains.user.schemas.update import UserPasswordUpdate

from .router import router


@router.post("/reset-password")
async def create_account_password_reset_authorization(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    email_client: Annotated[FastMail, Depends(get_email_client)],
    background_tasks: BackgroundTasks,
    authorization_create: AuthAccountPasswordResetAuthorizationCreate,
) -> AuthAccountPasswordResetAuthorizationCreated:
    """Send a account password reset authorization by email."""

    await auth_services.create_account_password_reset_authrorization(
        db=db,
        user_email=authorization_create.email,
        email_client=email_client,
        background_tasks=background_tasks,
        host_name=request.app.state.config.host_name,
        app_name=request.app.state.config.app_name,
    )

    return AuthAccountPasswordResetAuthorizationCreated()


@router.post("/reset-password/{authorization_code}")
async def apply_account_password_reset(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    email_client: Annotated[FastMail, Depends(get_email_client)],
    background_tasks: BackgroundTasks,
    authorization_code: UUID,
    user_password_update: UserPasswordUpdate,
) -> AuthAccountPasswordResetDone:
    """Apply the account password reset with `authorization_code`."""

    await auth_services.apply_account_password_reset(
        db=db,
        authorization_code=authorization_code,
        new_password=user_password_update.password,
        email_client=email_client,
        background_tasks=background_tasks,
        app_name=request.app.state.config.app_name,
        config=request.app.state.config.auth,
    )

    return AuthAccountPasswordResetDone()
