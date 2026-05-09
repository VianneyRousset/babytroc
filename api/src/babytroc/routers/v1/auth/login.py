from typing import Annotated

from fastapi import Depends, Form, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.auth import services as auth_services
from babytroc.domains.auth.schemas.credentials import UserCredentialsInfo
from babytroc.domains.auth.schemas.form import AuthPasswordForm
from babytroc.infrastructure.database import get_db_session

from .cookies import set_response_with_token_cookies
from .router import router


@router.post("/login")
async def login(
    request: Request,
    response: Response,
    form_data: Annotated[AuthPasswordForm, Form()],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserCredentialsInfo:
    """Get credentials from password."""

    credentials = await auth_services.login_user(
        db=db,
        email=form_data.username,
        password=form_data.password,
        config=request.app.state.config.auth,
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
