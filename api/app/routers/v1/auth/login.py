from typing import Annotated

from fastapi import Depends, Form, Request, Response
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.schemas.auth.credentials import UserCredentialsInfo
from app.schemas.auth.form import AuthPasswordForm

from .cookies import set_response_with_token_cookies
from .router import router


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
        validated=credentials.validated,
    )
