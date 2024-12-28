from typing import Annotated

from fastapi import APIRouter, Body, Path, Request, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.schemas.report.create import ReportCreate
from app.schemas.user.read import UserRead

router = APIRouter()

user_id_annotation = Annotated[
    int,
    Path(
        title="The ID of the user.",
        ge=0,
    ),
]


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
def get_user(
    request: Request,
    user_id: user_id_annotation,
    db: Session = Depends(get_db_session),
) -> UserRead:
    """Get user from id."""

    services.auth.check_auth(request)

    return services.user.get_user_by_id(
        db=db,
        user_id=user_id,
    )


@router.post("/{user_id}/report", status_code=status.HTTP_201_CREATED)
def report_user(
    request: Request,
    user_id: user_id_annotation,
    report_create: Annotated[
        ReportCreate,
        Body(title="Report fields."),
    ],
    db: Session = Depends(get_db_session),
):
    """Report user with `user_id`."""

    client_user_id = services.auth.check_auth(request)

    return services.user.report_user(
        db=db,
        user_id=user_id,
        reported_by_user_id=client_user_id,
        report_create=report_create,
    )
