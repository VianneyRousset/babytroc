from uuid import UUID

from fastapi import BackgroundTasks
from fastapi_mail import FastMail
from sqlalchemy import select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients import email
from app.config import Config
from app.errors.auth import (
    AuthAccountAlreadyValidatedError,
    AuthInvalidValidationCodeError,
)
from app.models.user import User
from app.pubsub import notify_user_async
from app.schemas.pubsub import PubsubMessageUpdatedAccountValidation


async def validate_user_account(
    db: AsyncSession,
    validation_code: UUID,
) -> None:
    """Mark user account with `validation_code` as validated."""

    stmt = (
        update(User)
        .where(User.validation_code == validation_code)
        .where(~User.validated)
        .values(validated=True)
        .returning(User)
    )

    try:
        user = (await db.execute(stmt)).unique().scalars().one()

    except NoResultFound as error:
        # check if validation code exists
        try:
            (
                await db.execute(
                    select(User.id).where(User.validation_code == validation_code)
                )
            ).unique().one()

        except NoResultFound:
            raise AuthInvalidValidationCodeError() from error

        # if the validation code does exist, then it be that the user account
        # is already validated
        raise AuthAccountAlreadyValidatedError() from error

    await notify_user_async(
        db=db,
        user_id=user.id,
        message=PubsubMessageUpdatedAccountValidation(
            validated=True,
        ),
    )


async def send_validation_email(
    db: AsyncSession,
    user_id: int,
    *,
    email_client: FastMail,
    background_tasks: BackgroundTasks,
    config: Config,
    check_validation_state: bool = True,
) -> None:
    """Send validation code to user with `user_id`."""

    # get user
    stmt = select(User).where(User.id == user_id)
    user = (await db.execute(stmt)).unique().scalars().one()

    # check if user account is already validated
    if check_validation_state and user.validated:
        raise AuthAccountAlreadyValidatedError()

    # send email
    email.send_account_validation_email(
        email_client=email_client,
        background_tasks=background_tasks,
        host_name=config.host_name,
        app_name=config.app_name,
        username=user.name,
        email=user.email,
        validation_code=user.validation_code,
    )
