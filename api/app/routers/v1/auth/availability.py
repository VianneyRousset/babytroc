from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.schemas.auth.api import AuthAccountAvailabilityApiQuery
from app.schemas.auth.availability import AuthAccountAvailability
from app.schemas.user.query import UserQueryFilter

from .router import router


@router.get("/available")
def get_account_availability(
    db: Annotated[Session, Depends(get_db_session)],
    query: Annotated[AuthAccountAvailabilityApiQuery, Query()],
) -> AuthAccountAvailability:
    """Get account availability to be created."""

    user_exists = services.user.get_user_exists(
        db=db,
        query_filter=UserQueryFilter(
            name=query.name,
            email=query.email,
        ),
    )

    return AuthAccountAvailability(available=not user_exists)
