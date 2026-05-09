from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.user import services as user_services
from app.infrastructure.database import get_db_session
from app.domains.auth.schemas.api import AuthAccountAvailabilityApiQuery
from app.domains.auth.schemas.availability import AuthAccountAvailability
from app.domains.user.schemas.query import UserReadQueryFilter

from .router import router


@router.get("/available")
async def get_account_availability(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    query: Annotated[AuthAccountAvailabilityApiQuery, Query()],
) -> AuthAccountAvailability:
    """Get account availability to be created."""

    user_exists = await user_services.list_users(
        db=db,
        query_filter=UserReadQueryFilter(
            name=query.name,
            email=query.email,
        ),
        limit=1,
    )

    return AuthAccountAvailability(available=not user_exists)
