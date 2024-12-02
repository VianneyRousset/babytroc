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


@router.get("/liked", status_code=status.HTTP_200_OK)
async def list_client_liked_items(
    request: Request,
    liked_before: Annotated[
        Optional[int],
        Query(
            title="Select item with liked date before the item with this id",
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
    """List client liked items ordered by save date."""

    client_user_id = services.auth.check_auth(request)

    return await services.items.list_user_liked_items(
        db=db,
        user_id=client_user_id,
        liked_before_item_id=liked_before,
        count=count,
    )


@router.post("/liked/{item_id}", status_code=status.HTTP_201_CREATED)
async def add_item_to_client_liked_items(
    request: Request,
    item_id: item_id_annotation,
    db: Session = Depends(get_db_session),
) -> ItemRead:
    """Add the specified item to client liked items."""

    client_user_id = services.auth.check_auth(request)

    return services.items.add_item_to_user_liked_items(
        db=db,
        user_id=client_user_id,
        item_id=item_id,
    )


@router.get("/liked/{item_id}", status_code=status.HTTP_200_OK)
async def get_client_liked_item_by_id(
    request: Request,
    item_id: item_id_annotation,
    db: Session = Depends(get_db_session),
) -> ItemRead:
    """Get client liked item by id."""

    client_user_id = services.auth.check_auth(request)

    return await services.items.get_user_liked_item_by_id(
        db=db,
        user_id=client_user_id,
        item_id=item_id,
    )


@router.delete("/liked/{item_id}", status_code=status.HTTP_200_OK)
async def remove_item_from_client_liked_items(
    request: Request,
    item_id: item_id_annotation,
    db: Session = Depends(get_db_session),
):
    """Remove the specified item from client liked items."""

    client_user_id = services.auth.check_auth(request)

    return services.items.remove_item_from_user_liked_items(
        db=db,
        user_id=client_user_id,
        item_id=item_id,
    )
