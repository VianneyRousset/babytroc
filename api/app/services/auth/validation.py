from uuid import UUID

from sqlalchemy.orm import Session

from app.clients import database
from app.errors.auth import AuthAccountAlreadyValidatedError
from app.pubsub import notify_user
from app.schemas.pubsub import PubsubMessageUpdatedAccountValidation


def validate_user_account(
    db: Session,
    validation_code: UUID,
) -> None:
    """Mark user account with `validation_code` as validated."""

    user = database.user.get_user_by_validation_code(db, validation_code)

    if user.validated:
        raise AuthAccountAlreadyValidatedError()

    database.user.mark_user_as_validated(db, user)

    notify_user(
        db=db,
        user_id=user.id,
        message=PubsubMessageUpdatedAccountValidation(
            validated=True,
        ),
    )
