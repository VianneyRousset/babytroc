from typing import Annotated

from fastapi import Depends, Request, Response
from fastapi.security.utils import get_authorization_scheme_param
from sqlalchemy.ext.asyncio import AsyncSession

from app import services
from app.database import get_db_async_session
from app.errors.auth import InvalidCredentialError
from app.schemas.auth.credentials import UserCredentialsInfo

from .cookies import set_response_with_token_cookies
from .router import router


@router.post("/refresh")
async def refresh_credentials(
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db_async_session)],
) -> UserCredentialsInfo:
    """Refresh credentials."""

    # trying get refresh_token from header or cookies
    authorization = request.headers.get("refresh_token")

    if authorization is None:
        authorization = request.cookies.get("refresh_token")

    scheme, token = get_authorization_scheme_param(authorization)

    if not authorization or scheme.lower() != "bearer":
        raise InvalidCredentialError()

    credentials = await services.auth.refresh_user_credentials(
        db=db,
        refresh_token=token,
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
