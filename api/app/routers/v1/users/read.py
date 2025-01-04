from typing import Annotated

from fastapi import Body, Request, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.schemas.report.create import ReportCreate
from app.schemas.user.read import UserRead

from .annotations import user_id_annotation
from .router import router


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
def get_user(
    request: Request,
    user_id: user_id_annotation,
    db: Annotated[Session, Depends(get_db_session)],
) -> UserRead:
    """Get user."""

    services.auth.check_auth(request)

    return services.user.get_user(
        db=db,
        user_id=user_id,
    )


# TODO check
@router.post("/{user_id}/report", status_code=status.HTTP_201_CREATED)
def report_user(
    request: Request,
    user_id: user_id_annotation,
    report_create: Annotated[
        ReportCreate,
        Body(title="Report fields."),
    ],
    db: Annotated[Session, Depends(get_db_session)],
):
    """Report user."""

    client_user_id = services.auth.check_auth(request)

    return services.user.report_user(
        db=db,
        user_id=user_id,
        reported_by_user_id=client_user_id,
        report_create=report_create,
    )
