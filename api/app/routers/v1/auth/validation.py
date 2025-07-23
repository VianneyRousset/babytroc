from typing import Annotated
from uuid import UUID

from fastapi import BackgroundTasks, Depends, Request
from fastapi_mail import FastMail
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.email import get_email_client
from app.schemas.auth.validation import AuthValidation, AuthValidationResendEmail

from .router import router
from .verification import oauth2_scheme, verify_request_credentials_no_validation_check


@router.post("/resend-validation-email")
def resend_validation_email(
    request: Request,
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db_session)],
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
    services.auth.send_validation_email(
        db=db,
        user_id=client_id,
        email_client=email_client,
        background_tasks=background_tasks,
        config=request.app.state.config,
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
