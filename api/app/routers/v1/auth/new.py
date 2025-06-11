from typing import Annotated

from fastapi import BackgroundTasks, Depends, Request, Response
from fastapi_mail import FastMail
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.email import get_email_client
from app.schemas.auth.credentials import UserCredentialsInfo
from app.schemas.user.create import UserCreate

from .cookies import set_response_with_token_cookies
from .router import router


@router.post("/new")
def create_user(
    db: Annotated[Session, Depends(get_db_session)],
    email_client: Annotated[FastMail, Depends(get_email_client)],
    background_tasks: BackgroundTasks,
    user_create: UserCreate,
    request: Request,
    response: Response,
) -> UserCredentialsInfo:
    """Create a new user."""

    services.user.create_user(
        db=db,
        email_client=email_client,
        app_name=request.app.state.config.app_name,
        background_tasks=background_tasks,
        user_create=user_create,
    )

    credentials = services.auth.login_user(
        db=db,
        email=user_create.email,
        password=user_create.password,
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
