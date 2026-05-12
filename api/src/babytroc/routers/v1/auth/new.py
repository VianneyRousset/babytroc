from typing import TYPE_CHECKING, Annotated

from fastapi import BackgroundTasks, Depends, Request, Response
from fastapi_mail import FastMail
from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.auth import services as auth_services
from babytroc.domains.auth.schemas.credentials import UserCredentialsInfo
from babytroc.domains.user import services as user_services
from babytroc.domains.user.schemas.create import UserCreate
from babytroc.infrastructure.database import get_db_session
from babytroc.infrastructure.email import get_email_client
from babytroc.shared.antibot import AntiBotMixin, verify_antibot
from babytroc.shared.rate_limit import make_rate_limit_dep

from .cookies import set_response_with_token_cookies
from .router import router

if TYPE_CHECKING:
    from babytroc.infrastructure.config import Config


class UserCreateRequest(AntiBotMixin, UserCreate):
    pass


rate_limit_signup = make_rate_limit_dep(
    key_prefix="signup",
    extract_config=lambda c: c.signup,
)


@router.post("/new")
async def create_user(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    email_client: Annotated[FastMail, Depends(get_email_client)],
    background_tasks: BackgroundTasks,
    user_create_request: UserCreateRequest,
    request: Request,
    response: Response,
    _rate_limited: Annotated[None, Depends(rate_limit_signup)],
) -> UserCredentialsInfo:
    """Create a new user."""

    config: Config = request.app.state.config
    await verify_antibot(user_create_request, config.cap)

    user_create = UserCreate.model_validate(
        user_create_request.model_dump(exclude={"cap_token", "website"}),
    )

    await user_services.create_user(
        db=db,
        email_client=email_client,
        host_name=config.host_name,
        app_name=config.app_name,
        background_tasks=background_tasks,
        user_create=user_create,
    )

    credentials = await auth_services.login_user(
        db=db,
        email=user_create.email,
        password=user_create.password,
        config=config.auth,
    )

    set_response_with_token_cookies(
        response=response,
        request=request,
        credentials=credentials,
    )

    return UserCredentialsInfo(
        expires_in=round(credentials.access_token_duration.total_seconds()),
        validated=credentials.validated,
    )
