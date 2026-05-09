# Compatibility shim — real module has moved to app.infrastructure.email_report
from app.infrastructure.email_report import *  # noqa: F401,F403
from app.infrastructure.email_report import send_report_email
