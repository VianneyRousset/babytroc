from datetime import datetime
from typing import Annotated, Optional

from fastapi import Path, Query, Request, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.schemas.item import ItemPreviewRead, ItemRead

from .me import router

item_id_annotation = (
    Annotated[
        int,
        Path(
            title="The ID of the item.",
            ge=0,
        ),
    ],
)


@router.get("/saved", status_code=status.HTTP_200_OK)
async def list_client_saved_items(
    request: Request,
    before: Annotated[
        Optional[datetime],
        Query(
            title="Select item with save date before the item with this id.",
        ),
    ] = None,
    count: Annotated[
        Optional[int],
        Query(
            title="Maximum number of items to return",
            ge=0,
        ),
    ] = None,
    db: Session = Depends(get_db_session),
) -> list[ItemPreviewRead]:
    """List client saved items ordered by inversed save date."""

    client_user_id = services.auth.check_auth(request)

    return await services.items.list_user_saved_items(
        db=db,
        user_id=client_user_id,
        saved_before_item_id=before,
        count=count,
    )


@router.post("/saved/{item_id}", status_code=status.HTTP_201_CREATED)
async def add_item_to_client_saved_items(
    request: Request,
    item_id: item_id_annotation,
    db: Session = Depends(get_db_session),
) -> ItemRead:
    """Add the specified item to client saved items."""

    client_user_id = services.auth.check_auth(request)

    return services.items.add_item_to_user_saved_items(
        db=db,
        user_id=client_user_id,
        item_id=item_id,
    )


@router.get("/saved/{item_id}", status_code=status.HTTP_200_OK)
async def get_client_saved_item_by_id(
    request: Request,
    item_id: item_id_annotation,
    db: Session = Depends(get_db_session),
) -> ItemRead:
    """Get client saved item by id."""

    client_user_id = services.auth.check_auth(request)

    return await services.items.get_user_saved_item_by_id(
        db=db,
        user_id=client_user_id,
        item_id=item_id,
    )


@router.delete("/saved/{item_id}", status_code=status.HTTP_200_OK)
async def remove_item_from_client_saved_items(
    request: Request,
    item_id: item_id_annotation,
    db: Session = Depends(get_db_session),
):
    """Remove the specified item from client saved items."""

    client_user_id = services.auth.check_auth(request)

    return services.items.remove_item_from_user_saved_items(
        db=db,
        user_id=client_user_id,
        item_id=item_id,
    )
