from sqlalchemy.orm import Session

from app.clients import database


def delete_user(
    db: Session,
    user_id: int,
) -> None:
    """Delete user with `user_id`."""

    # get user from database
    user = database.user.get_user(
        db=db,
        user_id=user_id,
    )

    # delete user from database
    database.user.delete_user(
        db=db,
        user=user,
    )
