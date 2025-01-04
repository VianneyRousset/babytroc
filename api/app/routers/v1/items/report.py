from typing import Annotated

from fastapi import Body, Request, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.schemas.report.create import ReportCreate

from .annotations import item_id_annotation
from .router import router


@router.post("/{item_id}/report", status_code=status.HTTP_201_CREATED)
def report_item(
    request: Request,
    item_id: item_id_annotation,
    report_create: Annotated[
        ReportCreate,
        Body(title="Report creation fields."),
    ],
    db: Annotated[Session, Depends(get_db_session)],
):
    """Report the specified item."""

    services.auth.check_auth(request)
