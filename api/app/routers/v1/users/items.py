from typing import Annotated

from fastapi import Depends, Query, Request, Response, status
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.schemas.item.api import ItemApiQuery
from app.schemas.item.preview import ItemPreviewRead
from app.schemas.item.query import ItemQueryFilter
from app.schemas.item.read import ItemRead

from .annotations import item_id_annotation, user_id_annotation
from .router import router


@router.get("/{user_id}/items", status_code=status.HTTP_200_OK)
def list_items_owned_by_user(
    request: Request,
    response: Response,
    user_id: user_id_annotation,
    query: Annotated[ItemApiQuery, Query()],
    db: Annotated[Session, Depends(get_db_session)],
) -> list[ItemPreviewRead]:
    """List items owned by user."""

    result = services.item.list_items(
        db=db,
        query_filter=ItemQueryFilter.model_validate(
            {
                **query.item_query_filter.model_dump(),
                "owner_id": user_id,
            }
        ),
        page_options=query.item_query_page_options,
    )

    result.set_response_headers(response, request)

    return result.data


@router.get("/{user_id}/items/{item_id}", status_code=status.HTTP_200_OK)
def get_client_item_by_id(
    request: Request,
    user_id: user_id_annotation,
    item_id: item_id_annotation,
    db: Annotated[Session, Depends(get_db_session)],
) -> ItemRead:
    """Get user's item by id."""

    return services.item.get_item(
        db=db,
        item_id=item_id,
        query_filter=ItemQueryFilter(
            owner_id=user_id,
        ),
    )
