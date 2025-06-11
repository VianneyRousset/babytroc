from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.schemas.auth.validation import AuthValidation, AuthValidationResendEmail

from .router import router


@router.post("/resend-validation-email")
def resend_validation_email() -> AuthValidationResendEmail:
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
