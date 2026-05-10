from email.message import Message

from fastapi_mail import ConnectionConfig, FastMail
from pydantic import SecretStr

from babytroc.infrastructure.email_contact import send_contact_email


def _html_body(msg: Message) -> str:
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            payload = part.get_payload(decode=True)
            assert isinstance(payload, bytes)
            charset = part.get_content_charset() or "utf-8"
            return payload.decode(charset)
    err = "no text/html part found"
    raise AssertionError(err)


def _fastmail() -> FastMail:
    return FastMail(
        ConnectionConfig(
            MAIL_USERNAME="u",
            MAIL_PASSWORD=SecretStr("p"),
            MAIL_PORT=587,
            MAIL_SERVER="smtp.test",
            MAIL_FROM="noreply@example.com",
            MAIL_FROM_NAME="Test",
            MAIL_STARTTLS=False,
            MAIL_SSL_TLS=True,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=False,
            SUPPRESS_SEND=1,
        )
    )


async def test_send_contact_email_recipient_is_contact_email():
    client = _fastmail()
    with client.record_messages() as outbox:
        await send_contact_email(
            client,
            app_name="Babytroc",
            contact_email="contact@babytroc.ch",
            submitter_name="Alice",
            submitter_email="alice@example.com",
            subject="Hello",
            message="Hi there",
            authenticated_user_id=None,
        )
    assert len(outbox) == 1
    msg = outbox[0]
    assert "contact@babytroc.ch" in msg["To"]


async def test_send_contact_email_subject_has_app_prefix():
    client = _fastmail()
    with client.record_messages() as outbox:
        await send_contact_email(
            client,
            app_name="Babytroc",
            contact_email="contact@babytroc.ch",
            submitter_name="Alice",
            submitter_email="alice@example.com",
            subject="Question",
            message="Hi",
            authenticated_user_id=None,
        )
    assert outbox[0]["Subject"] == "[Babytroc] Contact: Question"


async def test_send_contact_email_reply_to_set_to_submitter():
    client = _fastmail()
    with client.record_messages() as outbox:
        await send_contact_email(
            client,
            app_name="Babytroc",
            contact_email="contact@babytroc.ch",
            submitter_name="Alice",
            submitter_email="alice@example.com",
            subject="x",
            message="y",
            authenticated_user_id=None,
        )
    assert "alice@example.com" in outbox[0]["Reply-To"]


async def test_send_contact_email_escapes_html_in_message():
    client = _fastmail()
    with client.record_messages() as outbox:
        await send_contact_email(
            client,
            app_name="Babytroc",
            contact_email="contact@babytroc.ch",
            submitter_name="<b>Eve</b>",
            submitter_email="eve@example.com",
            subject="x",
            message="<script>alert(1)</script>",
            authenticated_user_id=None,
        )
    body = _html_body(outbox[0])
    assert "<script>alert(1)</script>" not in body
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in body
    assert "<b>Eve</b>" not in body
    assert "&lt;b&gt;Eve&lt;/b&gt;" in body


async def test_send_contact_email_renders_user_id_when_authenticated():
    client = _fastmail()
    with client.record_messages() as outbox:
        await send_contact_email(
            client,
            app_name="Babytroc",
            contact_email="contact@babytroc.ch",
            submitter_name="Alice",
            submitter_email="alice@example.com",
            subject="x",
            message="y",
            authenticated_user_id=42,
        )
    body = _html_body(outbox[0])
    assert "Authenticated user ID:</b> 42" in body


async def test_send_contact_email_renders_dash_when_anonymous():
    client = _fastmail()
    with client.record_messages() as outbox:
        await send_contact_email(
            client,
            app_name="Babytroc",
            contact_email="contact@babytroc.ch",
            submitter_name="Alice",
            submitter_email="alice@example.com",
            subject="x",
            message="y",
            authenticated_user_id=None,
        )
    body = _html_body(outbox[0])
    assert "Authenticated user ID:</b> —" in body
