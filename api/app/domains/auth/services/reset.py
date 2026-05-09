from uuid import UUID

from fastapi import BackgroundTasks
from fastapi_mail import FastMail
from sqlalchemy import delete, func, insert, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.auth.errors import AuthUnauthorizedAccountPasswordResetError
from app.domains.auth.models import AuthAccountPasswordResetAuthorization
from app.domains.user.models import User
from app.domains.user.services import get_user_by_email_private
from app.infrastructure.config import AuthConfig
from app.infrastructure.email_auth import send_account_password_reset_authorization
from app.shared.hash import HashedStr


async def create_account_password_reset_authrorization(
    db: AsyncSession,
    user_email: str,
    email_client: FastMail,
    background_tasks: BackgroundTasks,
    host_name: str,
    app_name: str,
    send_email: bool = True,
) -> None:
    """Create a password reset authrorization."""

    # get user
    user = await get_user_by_email_private(db, user_email)

    stmt = (
        insert(AuthAccountPasswordResetAuthorization)
        .values(user_id=user.id)
        .returning(AuthAccountPasswordResetAuthorization.authorization_code)
    )

    # create password reset authorization
    authorization_code = (await db.execute(stmt)).unique().scalar_one()

    if send_email:
        send_account_password_reset_authorization(
            email_client=email_client,
            background_tasks=background_tasks,
            host_name=host_name,
            app_name=app_name,
            username=user.name,
            email=user.email,
            authorization_code=authorization_code,
        )


async def apply_account_password_reset(
    db: AsyncSession,
    authorization_code: UUID,
    new_password: str | HashedStr,
    email_client: FastMail,
    background_tasks: BackgroundTasks,
    app_name: str,
    config: AuthConfig,
    send_email: bool = True,
) -> None:
    """Update account password using password reset authorization."""

    new_password = HashedStr(new_password)

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
        user_id = (await db.execute(consume_authorization_stmt)).unique().scalar_one()

    except NoResultFound as error:
        raise AuthUnauthorizedAccountPasswordResetError() from error

    # update user password
    update_password_stmt = (
        update(User)
        .values(password_hash=new_password)
        .where(User.id == user_id)
        .returning(User)
    )
    (await db.execute(update_password_stmt)).unique().one()
