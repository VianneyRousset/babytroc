from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.schemas.auth.validation import AuthValidation

from .router import router


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
