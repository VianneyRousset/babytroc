from typing import Annotated

from fastapi import Body, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.report.schemas.create import ReportCreate
from app.domains.user import services as user_services
from app.domains.user.schemas.read import UserRead
from app.infrastructure.cache import get_cache
from app.infrastructure.cache_client import Cache
from app.infrastructure.database import get_db_session
from app.routers.v1.auth import client_id_annotation

from .annotations import user_id_annotation
from .router import router


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_user(
    user_id: user_id_annotation,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    cache: Annotated[Cache, Depends(get_cache)],
) -> UserRead:
    """Get user."""

    return await user_services.get_user(
        db=db,
        user_id=user_id,
        cache=cache,
    )


# TODO check
@router.post("/{user_id}/report", status_code=status.HTTP_201_CREATED)
async def report_user(
    client_id: client_id_annotation,
    user_id: user_id_annotation,
    report_create: Annotated[
        ReportCreate,
        Body(title="Report fields."),
    ],
    db: Annotated[AsyncSession, Depends(get_db_session)],
):
    """Report user."""

    return await user_services.report_user(
        db=db,
        user_id=user_id,
        reported_by_user_id=client_id,
        report_create=report_create,
    )
