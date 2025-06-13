import os
from typing import Annotated

from fastapi import Depends, Request, WebSocket
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param

from app import services
from app.config import AuthConfig
from app.errors.auth import InvalidCredentialError
from app.schemas.auth.data import UserAccessTokenData

# TODO avoid this hack
# hack to include root_path into tokenUrl
# https://github.com/fastapi/fastapi/discussions/6045#discussioncomment-5443337
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{os.environ.get('API_PREFIX') or ''}/v1/auth/login",
    auto_error=False,
)


def verify_request_credentials(
    request: Request,
    token: Annotated[str | None, Depends(oauth2_scheme)],
) -> int:
    """Verify access token and return client user id."""

    token_data = get_and_verify_token(
        token=token,
        cookies=request.cookies,
        config=request.app.state.config.auth,
    )

    if not token_data.validated:
        raise InvalidCredentialError()

    return token_data.sub


def verify_request_credentials_no_validation_check(
    request: Request,
    token: Annotated[str | None, Depends(oauth2_scheme)],
) -> int:
    """Verify access token  without check if the account has been validated."""

    token_data = get_and_verify_token(
        token=token,
        cookies=request.cookies,
        config=request.app.state.config.auth,
    )

    return token_data.sub


def verify_websocket_credentials(
    websocket: WebSocket,
) -> int:
    """Verify access token and return client user id."""

    token_data = get_and_verify_token(
        token=None,
        cookies=websocket.cookies,
        config=websocket.app.state.config.auth,
    )

    if not token_data.validated:
        raise InvalidCredentialError()

    return token_data.sub


def verify_websocket_credentials_no_validation_check(
    websocket: WebSocket,
) -> int:
    """Verify access token and return client user id."""

    token_data = get_and_verify_token(
        token=None,
        cookies=websocket.cookies,
        config=websocket.app.state.config.auth,
    )

    return token_data.sub


def get_and_verify_token(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    cookies: dict[str, str],
    config: AuthConfig,
) -> UserAccessTokenData:
    # no "Authorization" header, let check the cookies
    if token is None:
        authorization = cookies.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)

        if not authorization or scheme.lower() != "bearer":
            raise InvalidCredentialError()

        token = param

    return services.auth.verify_access_token(
        token=token,
        config=config,
    )
