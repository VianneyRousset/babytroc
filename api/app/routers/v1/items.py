from typing import Annotated, Optional

from fastapi import APIRouter, Body, Path, Query, Request, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.schemas.item import ItemPreviewRead, ItemRead
from app.schemas.report import ReportCreate

router = APIRouter()


item_id_annotation = (
    Annotated[
        int,
        Path(
            title="The ID of the item to report",
            ge=0,
        ),
    ],
)


@router.get("", status_code=status.HTTP_200_OK)
def list_items(
    request: Request,
    terms: Annotated[
        Optional[list[str]],
        Query(
            title="Select items names and descriptions with the given search term",
            description="The terms are given as a list of words separated by `+`.",
            regex=r"^[a-zA-Z]+(?:\+[a-zA-Z]+)*$",
        ),
    ] = None,
    before: Annotated[
        Optional[int],
        Query(
            title="Select item with creation date before the item with this id",
        ),
    ] = None,
    count: Annotated[
        Optional[int],
        Query(
            title="Maximum number of items to return",
            ge=0,
        ),
    ] = None,
    age_min: Annotated[
        Optional[int],
        Query(
            title="Select items with targeted age more or equal `age_min` months",
            ge=0,
        ),
    ] = None,
    age_max: Annotated[
        Optional[int],
        Query(
            title="Select items with targeted age less or equal `age_max` months",
            ge=0,
        ),
    ] = None,
    regions: Annotated[
        Optional[list[int]],
        Query(title="Select items in the given regions."),
    ] = None,
    db: Session = Depends(get_db_session),
) -> list[ItemPreviewRead]:
    """List items ordered by inversed creation date."""

    client_user_id = services.auth.check_auth(request)

    return services.item.list_items(
        db=db,
        client_user_id=client_user_id,
        terms=terms,
        created_before_item_id=before,
        count=count,
        targeted_age=[age_min, age_max],
        regions=regions,
    )


@router.get("/{item_id}", status_code=status.HTTP_200_OK)
def get_item_by_id(
    request: Request,
    item_id: item_id_annotation,
    db: Session = Depends(get_db_session),
) -> ItemRead:
    """Get item."""

    client_user_id = services.auth.check_auth(request)

    return services.item.get_item_by_id_for_client(
        db=db,
        client_user_id=client_user_id,
        item_id=item_id,
    )


@router.post("/{item_id}/report", status_code=status.HTTP_201_CREATED)
def report_item(
    request: Request,
    item_id: item_id_annotation,
    report_create: Annotated[
        ReportCreate,
        Body(title="Report fields."),
    ],
    db: Session = Depends(get_db_session),
):
    """Report the specified item."""

    client_user_id = services.auth.check_auth(request)

    return services.item.report_item(
        db=db,
        item_id=item_id,
        client_user_id=client_user_id,
        report_create=report_create,
    )
