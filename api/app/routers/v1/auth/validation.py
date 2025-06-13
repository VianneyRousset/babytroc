from typing import Annotated
from uuid import UUID

from fastapi import BackgroundTasks, Depends, Request
from fastapi_mail import FastMail
from sqlalchemy.orm import Session

from app import services
from app.clients import database, email
from app.database import get_db_session
from app.email import get_email_client
from app.errors.auth import AuthAccountAlreadyValidatedError
from app.schemas.auth.validation import AuthValidation, AuthValidationResendEmail

from .router import router
from .verification import oauth2_scheme, verify_request_credentials


@router.post("/resend-validation-email")
def resend_validation_email(
    request: Request,
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db_session)],
    email_client: Annotated[FastMail, Depends(get_email_client)],
    background_tasks: BackgroundTasks,
) -> AuthValidationResendEmail:
    """Send a new account validation email."""

    user_id = verify_request_credentials(
        request=request,
        token=token,
        check_validated=False,
    )

    user = database.user.get_user(db, user_id)

    if user.validated:
        raise AuthAccountAlreadyValidatedError()

    email.send_account_validation_email(
        email_client=email_client,
        background_tasks=background_tasks,
        app_name=request.app.state.config.app_name,
        username=user.name,
        email=user.email,
        validation_code=user.validation_code,
    )

    return AuthValidationResendEmail(result="ok")


@router.post("/validate/{validation_code}")
def validate_user_account(
    db: Annotated[Session, Depends(get_db_session)],
    validation_code: UUID,
) -> AuthValidation:
    """Validate user account."""

    services.auth.validate_user_account(
        db=db,
        validation_code=validation_code,
    )

    return AuthValidation(result="ok")
