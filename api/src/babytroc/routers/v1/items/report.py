from typing import Annotated

from fastapi import Body, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.item import services as item_services
from babytroc.domains.report.schemas.create import ReportCreate
from babytroc.infrastructure.database import get_db_session
from babytroc.routers.v1.auth import client_id_annotation

from .annotations import item_id_annotation
from .router import router


@router.post("/{item_id}/report", status_code=status.HTTP_201_CREATED)
async def report_item(
    client_id: client_id_annotation,
    item_id: item_id_annotation,
    report_create: Annotated[
        ReportCreate,
        Body(title="Report creation fields."),
    ],
    db: Annotated[AsyncSession, Depends(get_db_session)],
):
    """Report the specified item."""
    return await item_services.report_item(
        db=db,
        item_id=item_id,
        reported_by_user_id=client_id,
        report_create=report_create,
    )
