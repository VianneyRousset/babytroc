from fastapi import BackgroundTasks
from fastapi_mail import FastMail
from sqlalchemy import insert
from sqlalchemy.orm import Session

from app.clients import email
from app.models.user import User
from app.schemas.user.create import UserCreate
from app.schemas.user.private import UserPrivateRead
from app.services.auth import hash_password


def create_user(
    db: Session,
    email_client: FastMail,
    background_tasks: BackgroundTasks,
    host_name: str,
    app_name: str,
    user_create: UserCreate,
    validated: bool = False,
    send_validation_email: bool = True,
) -> UserPrivateRead:
    """Create a user."""

    # insert user
    stmt = (
        insert(User)
        .values(
            **{
                **user_create.model_dump(exclude={"password"}),
                "password_hash": hash_password(user_create.password),
            }
        )
        .returning(User)
    )

    user = db.execute(stmt).unique().scalars().one()

    if send_validation_email:
        email.send_account_validation_email(
            email_client=email_client,
            background_tasks=background_tasks,
            host_name=host_name,
            app_name=app_name,
            username=user.name,
            email=user.email,
            validation_code=user.validation_code,
        )

    return UserPrivateRead.model_validate(user)


def create_many_users_without_validation(
    db: Session,
    user_creates: list[UserCreate],
    validated: bool = False,
) -> list[UserPrivateRead]:
    """Create many user without sending a validation email."""

    # insert users
    stmt = (
        insert(User)
        .values(
            [
                {
                    **user_create.model_dump(exclude={"password"}),
                    "password_hash": hash_password(user_create.password),
                }
                for user_create in user_creates
            ]
        )
        .returning(User)
    )

    # execute
    return [
        UserPrivateRead.model_validate(user)
        for user in db.execute(stmt).unique().scalars().all()
    ]
