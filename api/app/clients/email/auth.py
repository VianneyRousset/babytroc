from uuid import UUID

from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, MessageType
from pydantic import EmailStr


def send_account_validation_email(
    email_client: FastMail,
    background_tasks: BackgroundTasks,
    *,
    app_name: str,
    username: str,
    email: EmailStr,
    validation_code: UUID,
):
    message = MessageSchema(
        subject=f"{app_name} - Confirmer votre nouveau compte",
        recipients=[email],
        body=f"Confirm ton compte avec le validation code: {validation_code}",
        subtype=MessageType.plain,
    )

    background_tasks.add_task(email_client.send_message, message)


def send_account_password_reset_authorization(
    email_client: FastMail,
    background_tasks: BackgroundTasks,
    *,
    app_name: str,
    username: str,
    email: EmailStr,
    authorization_code: UUID,
):
    message = MessageSchema(
        subject=f"{app_name} - Réinitialiser votre mot de passe",
        recipients=[email],
        body=(
            "Réinitialiser votre mot de passe avec le code suivant: "
            f"{authorization_code}"
        ),
        subtype=MessageType.plain,
    )

    background_tasks.add_task(email_client.send_message, message)
