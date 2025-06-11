from uuid import UUID

from sqlalchemy.orm import Session

from app.clients import database


def validate_user_account(
    db: Session,
    validation_code: UUID,
) -> None:
    """Mark user account with `validation_code` as validated."""

    user = database.user.get_user_by_validation_code(db, validation_code)

    database.user.mark_user_as_validated(db, user)
