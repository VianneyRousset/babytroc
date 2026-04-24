from fastapi_mail import FastMail


def get_email_client() -> FastMail:
    return _email_client


_email_client: FastMail


def init_email_dependency(email_client: FastMail) -> None:
    global _email_client  # noqa: PLW0603
    _email_client = email_client
