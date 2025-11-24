from typing import Annotated

from fastapi import Body, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_async_session
from app.routers.v1.auth import client_id_annotation
from app.schemas.report.create import ReportCreate

from .annotations import item_id_annotation
from .router import router


@router.post("/{item_id}/report", status_code=status.HTTP_201_CREATED)
def report_item(
    client_id: client_id_annotation,
    item_id: item_id_annotation,
    report_create: Annotated[
        ReportCreate,
        Body(title="Report creation fields."),
    ],
    db: Annotated[AsyncSession, Depends(get_db_async_session)],
):
    """Report the specified item."""
    raise NotImplementedError()
