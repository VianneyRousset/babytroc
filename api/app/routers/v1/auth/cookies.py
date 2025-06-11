from fastapi import Request, Response

from app.schemas.auth.credentials import UserCredentials


def set_response_with_token_cookies(
    request: Request,
    response: Response,
    credentials: UserCredentials,
) -> Response:
    """Set response cookies with token cookies."""

    access_token = credentials.access_token
    refresh_token = credentials.refresh_token

    # set access token http-only cookie
    set_authorization_cookie(
        value=f"Bearer {access_token}",
        request=request,
        response=response,
        max_age=round(credentials.access_token_duration.total_seconds()),
    )
    set_refresh_token_cookie(
        value=f"Bearer {refresh_token}",
        request=request,
        response=response,
        max_age=round(credentials.refresh_token_duration.total_seconds()),
    )

    return response


def reset_response_token_cookies(
    response: Response,
    request: Request,
) -> Response:
    """Set token cookies with an empty value."""

    # set access token http-only cookie
    set_authorization_cookie(
        value="",
        request=request,
        response=response,
        max_age=0,
    )
    set_refresh_token_cookie(
        value="",
        request=request,
        response=response,
        max_age=0,
    )

    return response


def get_root_path(request: Request):
    """Get root_path from `request`."""

    return request.scope.get("root_path") or ""


def get_use_secure(request: Request):
    """Returns True if the cookies must be secure."""

    return not request.app.state.config.test


def set_authorization_cookie(
    value: str,
    *,
    request: Request,
    response: Response,
    max_age: int,
):
    response.set_cookie(
        key="Authorization",
        value=value,
        httponly=True,
        samesite="strict",
        max_age=max_age,
        secure=get_use_secure(request),
    )


def set_refresh_token_cookie(
    value: str,
    *,
    request: Request,
    response: Response,
    max_age: int,
):
    root_path = get_root_path(request)
    response.set_cookie(
        key="refresh_token",
        value=value,
        httponly=True,
        samesite="strict",
        path=f"{root_path}/v1/auth/refresh",
        max_age=max_age,
        secure=get_use_secure(request),
    )
