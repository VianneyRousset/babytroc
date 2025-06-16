from uuid import UUID

from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, MessageType
from pydantic import EmailStr


def send_account_validation_email(
    email_client: FastMail,
    background_tasks: BackgroundTasks,
    *,
    host_name: str,
    app_name: str,
    username: str,
    email: EmailStr,
    validation_code: UUID,
):
    message = MessageSchema(
        subject=f"{app_name} - Confirmer votre nouveau compte",
        recipients=[email],
        body=(
            "Confirmez votre compte <b>Babytroc</b> en "
            f'<a href="https://{host_name}/me/account/validate'
            f'?code={validation_code}">cliquant ici</a>.'
        ),
        subtype=MessageType.html,
    )

    background_tasks.add_task(email_client.send_message, message)


def send_account_password_reset_authorization(
    email_client: FastMail,
    background_tasks: BackgroundTasks,
    *,
    host_name: str,
    app_name: str,
    username: str,
    email: EmailStr,
    authorization_code: UUID,
):
    message = MessageSchema(
        subject=f"{app_name} - Réinitialiser votre mot de passe",
        recipients=[email],
        body=(
            "Réinitialisez votre mot de passe <b>Babytroc</b> en "
            f'<a href="https://{host_name}/me/account/reset-password'
            f'?code={authorization_code}">cliquant ici</a>.'
        ),
        subtype=MessageType.html,
    )

    background_tasks.add_task(email_client.send_message, message)
