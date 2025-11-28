from fastapi import BackgroundTasks
from fastapi_mail import FastMail
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients import email
from app.models.user import User
from app.schemas.user.create import UserCreate
from app.schemas.user.private import UserPrivateRead
from app.utils.hash import HashedStr

from .read import get_many_users_private, get_user_private


async def create_user(
    db: AsyncSession,
    email_client: FastMail,
    background_tasks: BackgroundTasks,
    host_name: str,
    app_name: str,
    user_create: UserCreate,
    validated: bool = False,
    send_validation_email: bool = True,
) -> UserPrivateRead:
    """Create a user."""

    db_users = await _create_many_users(
        db=db,
        user_creates=[user_create],
        validated=validated,
    )

    db_user = db_users[0]

    await db.flush()

    if send_validation_email:
        email.send_account_validation_email(
            email_client=email_client,
            background_tasks=background_tasks,
            host_name=host_name,
            app_name=app_name,
            username=db_user.name,
            email=db_user.email,
            validation_code=db_user.validation_code,
        )

    return await get_user_private(
        db=db,
        user_id=db_user.id,
    )


async def create_user_without_validation(
    db: AsyncSession,
    user_create: UserCreate,
    validated: bool = False,
) -> UserPrivateRead:
    """Create user without sending a validation email."""

    users = await create_many_users_without_validation(
        db=db,
        user_creates=[user_create],
        validated=validated,
    )

    return users[0]


async def create_many_users_without_validation(
    db: AsyncSession,
    user_creates: list[UserCreate],
    validated: bool = False,
) -> list[UserPrivateRead]:
    """Create many users without sending a validation email."""

    users = await _create_many_users(
        db=db,
        user_creates=user_creates,
        validated=validated,
    )

    await db.flush()

    return await get_many_users_private(
        db=db,
        user_ids={user.id for user in users},
    )


async def _create_many_users(
    db: AsyncSession,
    user_creates: list[UserCreate],
    validated: bool = False,
) -> list[User]:
    """Create many db users."""

    # insert users
    stmt = (
        insert(User)
        .values(
            [
                {
                    **user_create.model_dump(
                        exclude={"password"},
                        exclude_none=True,
                    ),
                    "password_hash": HashedStr(user_create.password),
                    "validated": validated,
                }
                for user_create in user_creates
            ]
        )
        .returning(User)
    )

    res = await db.execute(stmt)
    users = list(res.unique().scalars().all())

    return users
