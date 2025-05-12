from typing import Annotated

from fastapi import Depends, Query, Request, Response, status
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.routers.v1.auth import client_id_annotation
from app.schemas.item.api import ItemApiQuery
from app.schemas.item.preview import ItemPreviewRead
from app.schemas.item.query import ItemQueryFilter
from app.schemas.item.read import ItemRead
from app.schemas.query import QueryPageOptions
from app.utils import set_query_param

from .annotations import item_id_annotation
from .router import router


@router.get("", status_code=status.HTTP_200_OK)
def list_items_owned_by_client(
    client_id: client_id_annotation,
    request: Request,
    response: Response,
    query: Annotated[ItemApiQuery, Query()],
    db: Annotated[Session, Depends(get_db_session)],
) -> list[ItemPreviewRead]:
    """List items owned by the client."""

    result = services.item.list_items(
        db=db,
        query_filter=ItemQueryFilter(
            owner_id=client_id,
            words=query.q,
            targeted_age_months=query.parsed_mo,
            regions=query.reg,
        ),
        page_options=QueryPageOptions(
            limit=query.n,
            order=["words_match", "item_id"],
            cursor={"words_match": query.cwm, "item_id": query.cid},
            desc=True,
        ),
    )

    query_params = request.query_params
    for k, v in result.next_cursor().items():
        # rename query parameters
        k = {
            "words_match": "cwm",
            "item_id": "cid",
        }[k]

        query_params = set_query_param(query_params, k, v)

    response.headers["Link"] = f'<{request.url.path}?{query_params}>; rel="next"'

    response.headers["X-Total-Count"] = str(result.total_count)

    return result.data


@router.get("/{item_id}", status_code=status.HTTP_200_OK)
def get_client_item_by_id(
    client_id: client_id_annotation,
    item_id: item_id_annotation,
    db: Annotated[Session, Depends(get_db_session)],
) -> ItemRead:
    """Get client's item by id."""

    return services.item.get_item(
        db=db,
        item_id=item_id,
        query_filter=ItemQueryFilter(
            owner_id=client_id,
        ),
    )
