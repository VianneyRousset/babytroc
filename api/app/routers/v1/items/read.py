from typing import Annotated

from fastapi import Depends, Query, Request, Response, status
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.schemas.item.api import ItemApiQuery
from app.schemas.item.preview import ItemPreviewRead
from app.schemas.item.query import (
    ItemMatchingWordsQueryPageCursor,
    ItemQueryFilter,
    ItemQueryPageCursor,
)
from app.schemas.item.read import ItemRead
from app.schemas.query import QueryPageOptions

from .annotations import item_id_annotation
from .router import router


@router.get("", status_code=status.HTTP_200_OK)
def list_items(
    request: Request,
    response: Response,
    query: Annotated[ItemApiQuery, Query()],
    query_cursor: Annotated[ItemMatchingWordsQueryPageCursor, Query()],
    db: Annotated[Session, Depends(get_db_session)],
) -> list[ItemPreviewRead]:
    """List items."""

    words = query.q

    if not words:
        result = services.item.list_items(
            db=db,
            query_filter=ItemQueryFilter.model_validate(query),
            page_options=QueryPageOptions(
                limit=query.n,
                cursor=ItemQueryPageCursor.model_validate(query_cursor),
            ),
        )

    result.set_response_headers(response, request)

    return result.data


@router.get("/{item_id}", status_code=status.HTTP_200_OK)
def get_item(
    item_id: item_id_annotation,
    db: Annotated[Session, Depends(get_db_session)],
) -> ItemRead:
    """Get item."""

    return services.item.get_item(
        db=db,
        item_id=item_id,
    )
