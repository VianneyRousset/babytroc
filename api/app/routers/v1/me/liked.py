from typing import Annotated

from fastapi import Path, Query, Request, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.schemas.item.preview import ItemPreviewRead
from app.schemas.item.query import ItemQueryFilter
from app.schemas.item.read import ItemRead
from app.schemas.query import QueryPageOptions

from .me import router

item_id_annotation = Annotated[
    int,
    Path(
        title="The ID of the item.",
        ge=0,
    ),
]


# TODO check pagination parameters
@router.get("/liked", status_code=status.HTTP_200_OK)
def list_items_liked_by_client(
    request: Request,
    page_options: Annotated[
        QueryPageOptions,
        Query(),
    ],
    db: Session = Depends(get_db_session),
) -> list[ItemPreviewRead]:
    """List client liked items."""

    client_user_id = services.auth.check_auth(request)

    return services.item.list_items(
        db=db,
        query_filter=ItemQueryFilter(
            liked_by_user_id=client_user_id,
        ),
        page_options=page_options,
    )


@router.post("/liked/{item_id}", status_code=status.HTTP_201_CREATED)
def add_item_to_client_liked_items(
    request: Request,
    item_id: item_id_annotation,
    db: Session = Depends(get_db_session),
):
    """Add the specified item to client liked items."""

    client_user_id = services.auth.check_auth(request)

    return services.item.like.add_item_to_user_liked_items(
        db=db,
        user_id=client_user_id,
        item_id=item_id,
    )


@router.get("/liked/{item_id}", status_code=status.HTTP_200_OK)
def get_client_liked_item_by_id(
    request: Request,
    item_id: item_id_annotation,
    db: Session = Depends(get_db_session),
) -> ItemRead:
    """Get client liked item by id."""

    client_user_id = services.auth.check_auth(request)

    return services.item.get_item(
        db=db,
        item_id=item_id,
        query_filter=ItemQueryFilter(
            liked_by_user_id=client_user_id,
        ),
    )


@router.delete("/liked/{item_id}", status_code=status.HTTP_200_OK)
def remove_item_from_client_liked_items(
    request: Request,
    item_id: item_id_annotation,
    db: Session = Depends(get_db_session),
):
    """Remove the specified item from client liked items."""

    client_user_id = services.auth.check_auth(request)

    services.item.like.remove_item_from_user_liked_items(
        db=db,
        user_id=client_user_id,
        item_id=item_id,
    )
