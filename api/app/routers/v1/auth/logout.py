from fastapi import Request, Response

from .cookies import reset_response_token_cookies
from .router import router


@router.post("/logout")
def logout(
    request: Request,
    response: Response,
) -> None:
    """Remove credentials cookies."""

    reset_response_token_cookies(
        response=response,
        request=request,
    )
