from fastapi import BackgroundTasks
from fastapi_mail import FastMail
from sqlalchemy.orm import Session

from app.clients import database, email
from app.schemas.user.create import UserCreate
from app.schemas.user.private import UserPrivateRead
from app.services.auth import hash_password


def create_user(
    db: Session,
    email_client: FastMail,
    background_tasks: BackgroundTasks,
    app_name: str,
    user_create: UserCreate,
    validated: bool = False,
    send_validation_email: bool = True,
) -> UserPrivateRead:
    """Create a user."""

    # insert new user in database
    user = database.user.create_user(
        db=db,
        email=user_create.email,
        name=user_create.name,
        password_hash=hash_password(user_create.password),
        avatar_seed=user_create.avatar_seed,
        validated=validated,
    )

    if send_validation_email:
        email.send_account_validation_email(
            email_client=email_client,
            background_tasks=background_tasks,
            app_name=app_name,
            username=user.name,
            email=user.email,
            validation_code=user.validation_code,
        )

    return UserPrivateRead.model_validate(user)


def create_user_without_validation(
    db: Session,
    user_create: UserCreate,
    validated: bool = False,
):
    # insert new user in database
    user = database.user.create_user(
        db=db,
        email=user_create.email,
        name=user_create.name,
        password_hash=hash_password(user_create.password),
        avatar_seed=user_create.avatar_seed,
        validated=validated,
    )

    return UserPrivateRead.model_validate(user)
