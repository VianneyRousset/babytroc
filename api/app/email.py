# Compatibility shim — real module has moved to app.infrastructure.email
from app.infrastructure.email import *  # noqa: F401,F403
from app.infrastructure.email import (
    get_email_client,
    init_email_dependency,
)
