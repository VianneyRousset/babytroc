from datetime import UTC, datetime
from uuid import UUID

from fastapi import BackgroundTasks
from fastapi_mail import FastMail
from sqlalchemy.orm import Session

from app.clients import database, email
from app.config import AuthConfig
from app.errors.auth import AuthUnauthorizedAccountPasswordResetError
from app.errors.base import NotFoundError
from app.models.auth import AuthAccountPasswordResetAuthorization

from .password import hash_password


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

    user = database.user.get_user_by_email(db, user_email)

    authorization = database.auth.create_account_password_reset_authorization(
        db=db,
        user_id=user.id,
    )

    if send_email:
        email.send_account_password_reset_authorization(
            email_client=email_client,
            background_tasks=background_tasks,
            host_name=host_name,
            app_name=app_name,
            username=user.name,
            email=user.email,
            authorization_code=authorization.authorization_code,
        )


def is_account_password_reset_authorization_expired(
    authorization_creation_date: datetime,
    config: AuthConfig,
) -> bool:
    """Returns True if `authorization_creation_date` is expired."""

    now = datetime.now(UTC)

    duration = config.account_password_reset_authorization_duration
    return now - authorization_creation_date > duration


def verify_account_password_reset_authorization(
    db: Session,
    authorization_code: UUID,
    config: AuthConfig,
) -> AuthAccountPasswordResetAuthorization:
    """Raise exception if the authorization_code is not valid."""

    try:
        authorization = database.auth.get_account_password_reset_authorization(
            db=db,
            authorization_code=authorization_code,
        )

        if authorization.invalidated:
            raise AuthUnauthorizedAccountPasswordResetError()

        if is_account_password_reset_authorization_expired(
            authorization_creation_date=authorization.creation_date,
            config=config,
        ):
            raise AuthUnauthorizedAccountPasswordResetError()

        return authorization

    except NotFoundError as error:
        raise AuthUnauthorizedAccountPasswordResetError() from error


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
    # verify authorization code
    authorization = verify_account_password_reset_authorization(
        db=db,
        authorization_code=authorization_code,
        config=config,
    )

    try:
        user = database.user.get_user(db, authorization.user_id)

    except NotFoundError as error:
        raise AuthUnauthorizedAccountPasswordResetError() from error

    # update user password
    database.user.update_user_password(
        db=db,
        user=user,
        password_hash=hash_password(new_password),
    )

    # remove authorization
    database.auth.delete_account_password_reset_authorization(
        db=db,
        authorization=authorization,
    )
