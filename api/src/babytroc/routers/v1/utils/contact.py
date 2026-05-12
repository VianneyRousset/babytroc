from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from fastapi.responses import Response
from pydantic import BaseModel, EmailStr, StringConstraints
from redis.asyncio import Redis

from babytroc.infrastructure.cap import verify_cap_token
from babytroc.infrastructure.email import get_email_client
from babytroc.infrastructure.email_contact import send_contact_email
from babytroc.infrastructure.redis_dep import get_redis
from babytroc.routers.v1.auth.verification import maybe_verify_request_credentials
from babytroc.shared.errors import BadRequestError
from babytroc.shared.rate_limit import RateLimiter

if TYPE_CHECKING:
    from babytroc.infrastructure.config import Config

router = APIRouter()


class ContactSubmit(BaseModel):
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
    cap_token: Annotated[str, StringConstraints(min_length=1, max_length=4096)]
    website: str = ""  # honeypot — bots fill, humans don't see


async def rate_limit_contact(
    request: Request,
    redis: Annotated[Redis, Depends(get_redis)],
    client_id: Annotated[int | None, Depends(maybe_verify_request_credentials)],
) -> None:
    """Production rate-limit dep for the contact endpoint.

    Lazily builds and caches a `RateLimiter` from `app.state.config.contact`
    on first invocation per app instance. Tests override this dep entirely
    via `app.dependency_overrides[rate_limit_contact] = <RateLimiter instance>`.
    """
    limiter: RateLimiter | None = getattr(request.app.state, "_contact_limiter", None)
    if limiter is None:
        config: Config = request.app.state.config
        limiter = RateLimiter(
            key_prefix="contact",
            anon_limit=config.contact.rate_limit.anon,
            auth_limit=config.contact.rate_limit.auth,
            window=config.contact.rate_limit.window,
        )
        request.app.state._contact_limiter = limiter
    await limiter(request=request, redis=redis, client_id=client_id)


@router.post("/contact", status_code=status.HTTP_204_NO_CONTENT)
async def submit_contact(
    payload: ContactSubmit,
    request: Request,
    background_tasks: BackgroundTasks,
    _rate_limited: Annotated[None, Depends(rate_limit_contact)],
    client_id: Annotated[int | None, Depends(maybe_verify_request_credentials)],
) -> Response:
    # 1. honeypot
    if payload.website:
        msg = "INVALID_SUBMISSION"
        raise BadRequestError(msg)

    # 2. cap captcha
    config: Config = request.app.state.config
    if not await verify_cap_token(config.cap, payload.cap_token):
        msg = "INVALID_SUBMISSION"
        raise BadRequestError(msg)

    # 3. enqueue email send
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
