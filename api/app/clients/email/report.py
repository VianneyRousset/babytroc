from fastapi_mail import FastMail, MessageSchema, MessageType

from app.enums import ReportType


async def send_report_email(
    email_client: FastMail,
    *,
    app_name: str,
    moderator_email: str,
    report_type: ReportType,
    reporter_name: str,
    description: str,
    context: str,
    saved_info: str,
) -> None:
    """Send a report notification email to moderators."""

    message = MessageSchema(
        subject=f"[{app_name}] New {report_type.name} report",
        recipients=[moderator_email],
        body=(
            f"<h2>New {report_type.name} report</h2>"
            f"<p><b>Reporter:</b> {reporter_name}</p>"
            f"<p><b>Description:</b> {description}</p>"
            f"<p><b>Context:</b> {context}</p>"
            f"<hr>"
            f"<h3>Saved info</h3>"
            f"<pre>{saved_info}</pre>"
        ),
        subtype=MessageType.html,
    )

    await email_client.send_message(message)
