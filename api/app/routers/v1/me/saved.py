from typing import Annotated

from fastapi import Depends, Query, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import services
from app.database import get_db_async_session
from app.routers.v1.auth import client_id_annotation
from app.schemas.item.api import SavedItemApiQuery
from app.schemas.item.preview import ItemPreviewRead
from app.schemas.item.query import ItemReadQueryFilter
from app.schemas.item.read import ItemRead

from .annotations import item_id_annotation
from .me import router

# CREATE


@router.post("/saved/{item_id}", status_code=status.HTTP_200_OK)
async def add_item_to_client_saved_items(
    client_id: client_id_annotation,
    request: Request,
    item_id: item_id_annotation,
    db: Annotated[AsyncSession, Depends(get_db_async_session)],
) -> None:
    """Add item to client saved items."""

    await services.item.save.add_item_to_user_saved_items(
        db=db,
        user_id=client_id,
        item_id=item_id,
    )


# READ


@router.get("/saved", status_code=status.HTTP_200_OK)
async def list_items_saved_by_client(
    client_id: client_id_annotation,
    request: Request,
    response: Response,
    query: Annotated[SavedItemApiQuery, Query()],
    db: Annotated[AsyncSession, Depends(get_db_async_session)],
) -> list[ItemPreviewRead]:
    """List items saved by client."""

    result = await services.item.list_items(
        db=db,
        query_filter=ItemReadQueryFilter.model_validate(
            {
                **query.item_select_query_filter.model_dump(),
                "saved_by_user_id": client_id,
            }
        ),
        page_options=query.item_query_page_options,
    )

    result.set_response_headers(response, request)

    return result.data


@router.get("/saved/{item_id}", status_code=status.HTTP_200_OK)
async def get_client_saved_item_by_id(
    client_id: client_id_annotation,
    item_id: item_id_annotation,
    db: Annotated[AsyncSession, Depends(get_db_async_session)],
) -> ItemRead:
    """Get item saved by client."""

    return await services.item.get_item(
        db=db,
        item_id=item_id,
        query_filter=ItemReadQueryFilter(
            saved_by_user_id=client_id,
        ),
    )


# DELETE


@router.delete("/saved/{item_id}", status_code=status.HTTP_200_OK)
async def remove_item_from_client_saved_items(
    client_id: client_id_annotation,
    item_id: item_id_annotation,
    db: Annotated[AsyncSession, Depends(get_db_async_session)],
) -> None:
    """Remove the specified item from client saved items."""

    return await services.item.save.remove_item_from_user_saved_items(
        db=db,
        user_id=client_id,
        item_id=item_id,
    )
