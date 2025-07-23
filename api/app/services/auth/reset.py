from uuid import UUID

from fastapi import BackgroundTasks
from fastapi_mail import FastMail
from sqlalchemy import delete, func, insert, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.clients import email
from app.config import AuthConfig
from app.errors.auth import AuthUnauthorizedAccountPasswordResetError
from app.models.auth import AuthAccountPasswordResetAuthorization
from app.models.user import User
from app.services.auth import hash_password
from app.services.user import get_user_by_email_private


def create_account_password_reset_authrorization(
    db: Session,
    user_email: str,
    email_client: FastMail,
    background_tasks: BackgroundTasks,
    host_name: str,
    app_name: str,
    send_email: bool = True,
) -> None:
    """Create a password reset authrorization."""

    # get user
    user = get_user_by_email_private(db, user_email)

    # create password reset authorization
    authorization_code = (
        db.execute(
            insert(AuthAccountPasswordResetAuthorization)
            .values(user_id=user.id)
            .returning(AuthAccountPasswordResetAuthorization.authorization_code)
        )
        .unique()
        .scalar_one()
    )

    if send_email:
        email.send_account_password_reset_authorization(
            email_client=email_client,
            background_tasks=background_tasks,
            host_name=host_name,
            app_name=app_name,
            username=user.name,
            email=user.email,
            authorization_code=authorization_code,
        )


def apply_account_password_reset(
    db: Session,
    authorization_code: UUID,
    new_password: str,
    email_client: FastMail,
    background_tasks: BackgroundTasks,
    app_name: str,
    config: AuthConfig,
    send_email: bool = True,
) -> None:
    """Update account password using password reset authorization."""

    # delete account password reset authorization and get its user id
    # the authorization must exist, not be invalidated and not expired
    consume_authorization_stmt = (
        delete(AuthAccountPasswordResetAuthorization)
        .where(
            AuthAccountPasswordResetAuthorization.authorization_code
            == authorization_code
        )
        .where(~AuthAccountPasswordResetAuthorization.invalidated)
        .where(
            func.now() - AuthAccountPasswordResetAuthorization.creation_date
            <= config.account_password_reset_authorization_duration
        )
        .returning(AuthAccountPasswordResetAuthorization.user_id)
    )

    try:
        # execute
        user_id = db.execute(consume_authorization_stmt).unique().scalar_one()

    except NoResultFound as error:
        raise AuthUnauthorizedAccountPasswordResetError() from error

    # update user password
    db.execute(
        update(User)
        .values(password_hash=hash_password(new_password))
        .where(User.id == user_id)
        .returning(User)
    ).unique().one()
