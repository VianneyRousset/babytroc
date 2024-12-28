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


@router.get("/saved", status_code=status.HTTP_200_OK)
def list_items_saved_by_client(
    request: Request,
    page_options: Annotated[
        QueryPageOptions,
        Query(),
    ],
    db: Session = Depends(get_db_session),
) -> list[ItemPreviewRead]:
    """List client saved items."""

    client_user_id = services.auth.check_auth(request)

    return services.saved.list_items(
        db=db,
        query_filter=ItemQueryFilter(
            saved_by_user_id=client_user_id,
        ),
        page_options=page_options,
    )


@router.post("/saved/{item_id}", status_code=status.HTTP_201_CREATED)
def add_item_to_client_saved_items(
    request: Request,
    item_id: item_id_annotation,
    db: Session = Depends(get_db_session),
) -> ItemRead:
    """Add the specified item to client saved items."""

    client_user_id = services.auth.check_auth(request)

    return services.item.save.add_item_to_user_saved_items(
        db=db,
        user_id=client_user_id,
        item_id=item_id,
    )


@router.get("/saved/{item_id}", status_code=status.HTTP_200_OK)
def get_client_saved_item_by_id(
    request: Request,
    item_id: item_id_annotation,
    db: Session = Depends(get_db_session),
) -> ItemRead:
    """Get client saved item by id."""

    client_user_id = services.auth.check_auth(request)

    return services.item.get_item(
        db=db,
        item_id=item_id,
        query_filter=ItemQueryFilter(
            saved_by_user_id=client_user_id,
        ),
    )


@router.delete("/saved/{item_id}", status_code=status.HTTP_200_OK)
def remove_item_from_client_saved_items(
    request: Request,
    item_id: item_id_annotation,
    db: Session = Depends(get_db_session),
):
    """Remove the specified item from client saved items."""

    client_user_id = services.auth.check_auth(request)

    return services.item.save.remove_item_from_user_saved_items(
        db=db,
        user_id=client_user_id,
        item_id=item_id,
    )
