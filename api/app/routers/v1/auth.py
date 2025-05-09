import os
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, Response, WebSocket
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.errors.auth import InvalidCredentialError
from app.schemas.auth.credentials import UserCredentials, UserCredentialsInfo
from app.schemas.auth.form import AuthPasswordForm

router = APIRouter()

# TODO avoid this hack
# hack to include root_path into tokenUrl
# https://github.com/fastapi/fastapi/discussions/6045#discussioncomment-5443337
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{os.environ.get('API_PREFIX') or ''}/v1/auth/login",
    auto_error=False,
)


def get_client_id(
    request: Request,
    token: Annotated[str | None, Depends(oauth2_scheme)],
) -> int:
    """Verify access token and return client user id."""

    # no "Authorization" header, let check the cookies
    if token is None:
        authorization = request.cookies.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)

        if not authorization or scheme.lower() != "bearer":
            raise InvalidCredentialError()

        token = param

    token_data = services.auth.verify_access_token(
        token=token,
        config=request.app.state.config.auth,
    )

    return token_data.sub


client_id_annotation = Annotated[int, Depends(get_client_id)]


def verify_websocket_credentials(
    websocket: WebSocket,
) -> int:
    """Verify access token and return client user id."""

    authorization = websocket.cookies.get("Authorization")
    scheme, token = get_authorization_scheme_param(authorization)

    if not authorization or scheme.lower() != "bearer":
        raise InvalidCredentialError()

    token_data = services.auth.verify_access_token(
        token=token,
        config=websocket.app.state.config.auth,
    )

    return token_data.sub


def set_response_with_token_cookies(
    response: Response,
    request: Request,
    credentials: UserCredentials,
) -> Response:
    """Set response cookies with token cookies."""

    access_token = credentials.access_token
    refresh_token = credentials.refresh_token
    root_path = request.scope.get("root_path") or ""
    secure = not request.app.state.config.test

    # set access token http-only cookie
    response.set_cookie(
        key="Authorization",
        value=f"Bearer {access_token}",
        httponly=True,
        samesite="strict",
        max_age=round(credentials.access_token_duration.total_seconds()),
        secure=secure,
    )

    # set refresh token http-only cookie
    response.set_cookie(
        key="refresh_token",
        value=f"Bearer {refresh_token}",
        httponly=True,
        samesite="strict",
        path=f"{root_path}/v1/auth/refresh",
        max_age=round(credentials.refresh_token_duration.total_seconds()),
        secure=secure,
    )

    return response


@router.post("/login")
def login(
    request: Request,
    response: Response,
    form_data: Annotated[AuthPasswordForm, Form()],
    db: Annotated[Session, Depends(get_db_session)],
) -> UserCredentialsInfo:
    """Get credentials from password."""

    credentials = services.auth.login_user(
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
    )


@router.post("/refresh")
def refresh_credentials(
    request: Request,
    response: Response,
    db: Annotated[Session, Depends(get_db_session)],
) -> UserCredentialsInfo:
    """Refresh credentials."""

    # trying get refresh_token from header or cookies
    authorization = request.headers.get("refresh_token")

    if authorization is None:
        authorization = request.cookies.get("refresh_token")

    scheme, token = get_authorization_scheme_param(authorization)

    if not authorization or scheme.lower() != "bearer":
        raise InvalidCredentialError()

    credentials = services.auth.refresh_user_credentials(
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
    )


@router.post("/logout")
def logout(
    request: Request,
    response: Response,
) -> None:
    """Remove credentials cookies."""

    root_path = request.scope.get("root_path") or ""
    secure = not request.app.state.config.test

    # set access token http-only cookie
    response.set_cookie(
        key="Authorization",
        value="",
        httponly=True,
        samesite="strict",
        max_age=0,
        secure=secure,
    )

    # set refresh token http-only cookie
    response.set_cookie(
        key="refresh_token",
        value="",
        httponly=True,
        samesite="strict",
        path=f"{root_path}/v1/auth/refresh",
        max_age=0,
        secure=secure,
    )
