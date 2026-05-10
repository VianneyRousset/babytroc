from html import escape

from fastapi_mail import FastMail, MessageSchema, MessageType
from pydantic import EmailStr, NameEmail


async def send_contact_email(
    email_client: FastMail,
    *,
    app_name: str,
    contact_email: str,
    submitter_name: str,
    submitter_email: EmailStr,
    subject: str,
    message: str,
    authenticated_user_id: int | None,
) -> None:
    """Forward a contact-form submission to the contact mailbox."""
    user_id_str = (
        str(authenticated_user_id) if authenticated_user_id is not None else "—"
    )
    msg = MessageSchema(
        subject=f"[{app_name}] Contact: {subject}",
        recipients=[NameEmail(name="Contact", email=contact_email)],
        reply_to=[NameEmail(name=submitter_name, email=submitter_email)],
        body=(
            "<h2>New contact form submission</h2>"
            f"<p><b>From:</b> {escape(submitter_name)} "
            f"&lt;{escape(submitter_email)}&gt;</p>"
            f"<p><b>Authenticated user ID:</b> {escape(user_id_str)}</p>"
            f"<p><b>Subject:</b> {escape(subject)}</p>"
            "<hr>"
            f"<pre>{escape(message)}</pre>"
        ),
        subtype=MessageType.html,
    )
    await email_client.send_message(msg)
