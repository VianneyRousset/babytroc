from typing import Annotated

from fastapi import Depends, Query, Request, Response, status
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.routers.v1.auth import client_id_annotation
from app.schemas.item.api import SavedItemApiQuery
from app.schemas.item.preview import ItemPreviewRead
from app.schemas.item.query import ItemQueryFilter
from app.schemas.item.read import ItemRead
from app.schemas.query import QueryPageOptions
from app.utils import set_query_param

from .annotations import item_id_annotation
from .me import router

# CREATE


@router.post("/saved/{item_id}", status_code=status.HTTP_200_OK)
def add_item_to_client_saved_items(
    client_id: client_id_annotation,
    request: Request,
    item_id: item_id_annotation,
    db: Annotated[Session, Depends(get_db_session)],
) -> ItemRead:
    """Add item to client saved items."""

    return services.item.save.add_item_to_user_saved_items(
        db=db,
        user_id=client_id,
        item_id=item_id,
    )


# READ


@router.get("/saved", status_code=status.HTTP_200_OK)
def list_items_saved_by_client(
    client_id: client_id_annotation,
    request: Request,
    response: Response,
    query: Annotated[SavedItemApiQuery, Query()],
    db: Annotated[Session, Depends(get_db_session)],
) -> list[ItemPreviewRead]:
    """List items saved by client."""

    result = services.item.list_items(
        db=db,
        query_filter=ItemQueryFilter(
            words=query.q,
            targeted_age_months=query.parsed_mo,
            saved_by_user_id=client_id,
        ),
        page_options=QueryPageOptions(
            order=["save_id", "item_id"],
            desc=True,
        ),
    )

    query_params = request.query_params
    for k, v in result.next_cursor().items():
        # rename query parameters
        k = {
            "words_match": "cwm",
            "save_id": "sid",
            "item_id": "cid",
        }[k]

        query_params = set_query_param(query_params, k, v)

    response.headers["Link"] = f'<{request.url.path}?{query_params}>; rel="next"'

    response.headers["X-Total-Count"] = str(result.total_count)

    return result.data


@router.get("/saved/{item_id}", status_code=status.HTTP_200_OK)
def get_client_saved_item_by_id(
    client_id: client_id_annotation,
    item_id: item_id_annotation,
    db: Annotated[Session, Depends(get_db_session)],
) -> ItemRead:
    """Get item saved by client."""

    return services.item.get_item(
        db=db,
        item_id=item_id,
        query_filter=ItemQueryFilter(
            saved_by_user_id=client_id,
        ),
    )


# DELETE


@router.delete("/saved/{item_id}", status_code=status.HTTP_200_OK)
def remove_item_from_client_saved_items(
    client_id: client_id_annotation,
    item_id: item_id_annotation,
    db: Annotated[Session, Depends(get_db_session)],
) -> ItemRead:
    """Remove the specified item from client saved items."""

    return services.item.save.remove_item_from_user_saved_items(
        db=db,
        user_id=client_id,
        item_id=item_id,
    )
