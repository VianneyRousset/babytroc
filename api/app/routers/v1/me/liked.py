from typing import Annotated

from fastapi import Depends, Query, Request, Response, status
from sqlalchemy.ext.asyncio.ext import AsyncSession

from app import services
from app.database import get_db_async_session
from app.routers.v1.auth import client_id_annotation
from app.schemas.item.api import LikedItemApiQuery
from app.schemas.item.preview import ItemPreviewRead
from app.schemas.item.query import ItemReadQueryFilter
from app.schemas.item.read import ItemRead

from .annotations import item_id_annotation
from .me import router

# CREATE


@router.post("/liked/{item_id}", status_code=status.HTTP_200_OK)
async def add_item_to_client_liked_items(
    client_id: client_id_annotation,
    item_id: item_id_annotation,
    db: Annotated[AsyncSession, Depends(get_db_async_session)],
) -> None:
    """Add the specified item to client liked items."""

    await services.item.like.add_item_to_user_liked_items(
        db=db,
        user_id=client_id,
        item_id=item_id,
    )


# READ


@router.get("/liked", status_code=status.HTTP_200_OK)
async def list_items_liked_by_client(
    client_id: client_id_annotation,
    request: Request,
    response: Response,
    query: Annotated[LikedItemApiQuery, Query()],
    db: Annotated[AsyncSession, Depends(get_db_async_session)],
) -> list[ItemPreviewRead]:
    """List items like by client."""

    result = await services.item.list_items(
        db=db,
        query_filter=ItemReadQueryFilter.model_validate(
            {
                **query.item_select_query_filter.model_dump(),
                "liked_by_user_id": client_id,
            }
        ),
    )

    result.set_response_headers(response, request)

    return result.data


@router.get("/liked/{item_id}", status_code=status.HTTP_200_OK)
async def get_client_liked_item_by_id(
    client_id: client_id_annotation,
    request: Request,
    item_id: item_id_annotation,
    db: Annotated[AsyncSession, Depends(get_db_async_session)],
) -> ItemRead:
    """Get item liked by client."""

    return await services.item.get_item(
        db=db,
        item_id=item_id,
        query_filter=ItemReadQueryFilter(
            liked_by_user_id=client_id,
        ),
    )


# DELETE


@router.delete("/liked/{item_id}", status_code=status.HTTP_200_OK)
async def remove_item_from_client_liked_items(
    client_id: client_id_annotation,
    item_id: item_id_annotation,
    db: Annotated[AsyncSession, Depends(get_db_async_session)],
) -> None:
    """Remove the specified item from client liked items."""

    await services.item.like.remove_item_from_user_liked_items(
        db=db,
        user_id=client_id,
        item_id=item_id,
    )
