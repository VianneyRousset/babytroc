# Compatibility shim — real module has moved to app.infrastructure.email_auth
from app.infrastructure.email_auth import *  # noqa: F401,F403
from app.infrastructure.email_auth import (
    send_account_password_reset_authorization,
    send_account_validation_email,
)
