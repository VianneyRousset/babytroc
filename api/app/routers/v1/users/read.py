from typing import Annotated

from fastapi import Body, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.routers.v1.auth import client_id_annotation
from app.schemas.report.create import ReportCreate
from app.schemas.user.read import UserRead

from .annotations import user_id_annotation
from .router import router


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
def get_user(
    user_id: user_id_annotation,
    db: Annotated[Session, Depends(get_db_session)],
) -> UserRead:
    """Get user."""

    return services.user.get_user(
        db=db,
        user_id=user_id,
    )


# TODO check
@router.post("/{user_id}/report", status_code=status.HTTP_201_CREATED)
def report_user(
    client_id: client_id_annotation,
    user_id: user_id_annotation,
    report_create: Annotated[
        ReportCreate,
        Body(title="Report fields."),
    ],
    db: Annotated[Session, Depends(get_db_session)],
):
    """Report user."""

    return services.user.report_user(
        db=db,
        user_id=user_id,
        reported_by_user_id=client_id,
        report_create=report_create,
    )
