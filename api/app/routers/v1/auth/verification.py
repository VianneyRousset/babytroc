import os
from typing import Annotated

from fastapi import Depends, Request, WebSocket
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param

from app import services
from app.errors.auth import InvalidCredentialError

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
    check_validated: bool = True,
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

    if check_validated and not token_data.validated:
        raise InvalidCredentialError()

    return token_data.sub


def verify_websocket_credentials(
    websocket: WebSocket,
    check_validated: bool = True,
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

    if check_validated and not token_data.validated:
        raise InvalidCredentialError()

    return token_data.sub
