from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, BackgroundTasks, Body, Depends, Request, status
from fastapi.responses import Response
from pydantic import BaseModel, EmailStr, StringConstraints

from babytroc.infrastructure.email import get_email_client
from babytroc.infrastructure.email_contact import send_contact_email
from babytroc.routers.v1.auth.verification import maybe_verify_request_credentials
from babytroc.shared.antibot import AntiBotMixin, verify_antibot
from babytroc.shared.rate_limit import make_rate_limit_dep

if TYPE_CHECKING:
    from babytroc.infrastructure.config import Config

router = APIRouter()


class ContactSubmit(AntiBotMixin, BaseModel):
    name: Annotated[
        str, StringConstraints(min_length=1, max_length=100, strip_whitespace=True)
    ]
    email: EmailStr
    subject: Annotated[
        str, StringConstraints(min_length=1, max_length=200, strip_whitespace=True)
    ]
    message: Annotated[
        str, StringConstraints(min_length=1, max_length=5000, strip_whitespace=True)
    ]


rate_limit_contact = make_rate_limit_dep(
    key_prefix="contact",
    extract_config=lambda c: c.contact.rate_limit,
)


@router.post("/contact", status_code=status.HTTP_204_NO_CONTENT)
async def submit_contact(
    payload: Annotated[ContactSubmit, Body()],
    request: Request,
    background_tasks: BackgroundTasks,
    _rate_limited: Annotated[None, Depends(rate_limit_contact)],
    client_id: Annotated[int | None, Depends(maybe_verify_request_credentials)],
) -> Response:
    config: Config = request.app.state.config
    await verify_antibot(payload, config.cap)

    email_client = get_email_client()
    background_tasks.add_task(
        send_contact_email,
        email_client,
        app_name=config.app_name,
        contact_email=config.contact.email,
        submitter_name=payload.name,
        submitter_email=payload.email,
        subject=payload.subject,
        message=payload.message,
        authenticated_user_id=client_id,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
