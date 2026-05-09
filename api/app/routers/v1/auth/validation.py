from typing import Annotated
from uuid import UUID

from fastapi import BackgroundTasks, Depends, Request
from fastapi_mail import FastMail
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.auth import services as auth_services
from app.domains.auth.schemas.validation import (
    AuthValidation,
    AuthValidationResendEmail,
)
from app.infrastructure.cache import get_cache
from app.infrastructure.cache_client import Cache
from app.infrastructure.database import get_db_session
from app.infrastructure.email import get_email_client

from .router import router
from .verification import oauth2_scheme, verify_request_credentials_no_validation_check


@router.post("/resend-validation-email")
async def resend_validation_email(
    request: Request,
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    email_client: Annotated[FastMail, Depends(get_email_client)],
    background_tasks: BackgroundTasks,
) -> AuthValidationResendEmail:
    """Send a new account validation email."""

    # get user id from credentials
    client_id = verify_request_credentials_no_validation_check(
        request=request,
        token=token,
    )

    # send email
    await auth_services.send_validation_email(
        db=db,
        user_id=client_id,
        email_client=email_client,
        background_tasks=background_tasks,
        config=request.app.state.config,
    )

    return AuthValidationResendEmail(result="ok")


@router.post("/validate/{validation_code}")
async def validate_user_account(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    validation_code: UUID,
    cache: Annotated[Cache, Depends(get_cache)],
) -> AuthValidation:
    """Validate user account."""

    await auth_services.validate_user_account(
        db=db,
        validation_code=validation_code,
        cache=cache,
    )

    return AuthValidation(result="ok")
