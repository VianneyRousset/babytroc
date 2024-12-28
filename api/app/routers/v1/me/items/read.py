from typing import Annotated

from fastapi import Query, Request, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.schemas.item.preview import ItemPreviewRead
from app.schemas.item.query import ItemQueryFilter
from app.schemas.item.read import ItemRead
from app.schemas.query import QueryPageOptions

from .annotations import item_id_annotation
from .router import router


# TODO check pagination parameters
@router.get("/items", status_code=status.HTTP_200_OK)
def list_items_owned_by_client(
    request: Request,
    page_options: Annotated[
        QueryPageOptions,
        Query(),
    ],
    db: Session = Depends(get_db_session),
) -> list[ItemPreviewRead]:
    """List items owned by the client."""

    client_user_id = services.auth.check_auth(request)

    return services.items.list_items(
        db=db,
        query_filter=ItemQueryFilter(
            owner_id=client_user_id,
        ),
        page_options=page_options,
    )


@router.get("/items/{item_id}", status_code=status.HTTP_200_OK)
def get_client_item_by_id(
    request: Request,
    item_id: item_id_annotation,
    db: Session = Depends(get_db_session),
) -> ItemRead:
    """Get client's item by id."""

    client_user_id = services.auth.check_auth(request)

    return services.items.get_user_item_by_id(
        db=db,
        owner_user_id=client_user_id,
        item_id=item_id,
    )
