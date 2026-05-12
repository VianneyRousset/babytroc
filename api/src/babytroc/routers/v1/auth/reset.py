from typing import TYPE_CHECKING, Annotated
from uuid import UUID

from fastapi import BackgroundTasks, Depends, Request
from fastapi_mail import FastMail
from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.auth import services as auth_services
from babytroc.domains.auth.schemas.create import (
    AuthAccountPasswordResetAuthorizationCreate,
)
from babytroc.domains.auth.schemas.reset import (
    AuthAccountPasswordResetAuthorizationCreated,
    AuthAccountPasswordResetDone,
)
from babytroc.domains.user.schemas.update import UserPasswordUpdate
from babytroc.infrastructure.database import get_db_session
from babytroc.infrastructure.email import get_email_client
from babytroc.shared.antibot import AntiBotMixin, verify_antibot
from babytroc.shared.rate_limit import make_rate_limit_dep

from .router import router

if TYPE_CHECKING:
    from babytroc.infrastructure.config import Config


class PasswordResetRequest(AntiBotMixin, AuthAccountPasswordResetAuthorizationCreate):
    pass


rate_limit_password_reset = make_rate_limit_dep(
    key_prefix="password_reset",
    extract_config=lambda c: c.password_reset,
)


@router.post("/reset-password")
async def create_account_password_reset_authorization(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    email_client: Annotated[FastMail, Depends(get_email_client)],
    background_tasks: BackgroundTasks,
    reset_request: PasswordResetRequest,
    _rate_limited: Annotated[None, Depends(rate_limit_password_reset)],
) -> AuthAccountPasswordResetAuthorizationCreated:
    """Send an account password reset authorization by email."""

    config: Config = request.app.state.config
    await verify_antibot(reset_request, config.cap)

    await auth_services.create_account_password_reset_authrorization(
        db=db,
        user_email=reset_request.email,
        email_client=email_client,
        background_tasks=background_tasks,
        host_name=config.host_name,
        app_name=config.app_name,
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
