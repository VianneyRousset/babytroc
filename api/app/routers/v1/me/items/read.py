from typing import Annotated

from fastapi import Depends, Query, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import services
from app.database import get_db_session
from app.routers.v1.auth import client_id_annotation
from app.schemas.item.api import ItemApiQuery
from app.schemas.item.preview import ItemPreviewRead
from app.schemas.item.query import ItemReadQueryFilter
from app.schemas.item.read import ItemRead

from .annotations import item_id_annotation
from .router import router


@router.get("", status_code=status.HTTP_200_OK)
async def list_items_owned_by_client(
    client_id: client_id_annotation,
    request: Request,
    response: Response,
    query: Annotated[ItemApiQuery, Query()],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[ItemPreviewRead]:
    """List items owned by the client."""

    result = await services.item.list_items(
        db=db,
        query_filter=ItemReadQueryFilter.model_validate(
            {
                **query.item_select_query_filter.model_dump(),
                "owner_id": client_id,
            }
        ),
        page_options=query.item_query_page_options,
    )

    result.set_response_headers(response, request)

    return result.data


@router.get("/{item_id}", status_code=status.HTTP_200_OK)
async def get_client_item_by_id(
    client_id: client_id_annotation,
    item_id: item_id_annotation,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ItemRead:
    """Get client's item by id."""

    return await services.item.get_item(
        db=db,
        item_id=item_id,
        query_filter=ItemReadQueryFilter(
            owner_id=client_id,
        ),
    )
