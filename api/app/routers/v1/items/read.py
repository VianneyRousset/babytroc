from typing import Annotated

from fastapi import Depends, Query, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import services
from app.database import get_db_session
from app.routers.v1.auth import maybe_client_id_annotation
from app.schemas.item.api import ItemMatchinWordsApiQuery
from app.schemas.item.preview import ItemPreviewRead
from app.schemas.item.read import ItemRead

from .annotations import item_id_annotation
from .router import router


@router.get("", status_code=status.HTTP_200_OK)
async def list_items(
    request: Request,
    response: Response,
    query: Annotated[ItemMatchinWordsApiQuery, Query()],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[ItemPreviewRead]:
    """List items."""

    # words fuzzy search
    if query.words:
        fuzzy_search_result = await services.item.list_items_matching_words(
            db=db,
            words=query.words,
            query_filter=query.item_select_query_filter,
            page_options=query.item_matching_words_query_page_options,
        )

        fuzzy_search_result.set_response_headers(response, request)

        return fuzzy_search_result.data

    result = await services.item.list_items(
        db=db,
        query_filter=query.item_select_query_filter,
        page_options=query.item_query_page_options,
    )

    result.set_response_headers(response, request)

    return result.data


@router.get("/{item_id}", status_code=status.HTTP_200_OK)
async def get_item(
    item_id: item_id_annotation,
    client_id: maybe_client_id_annotation,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ItemRead:
    """Get item."""

    return await services.item.get_item(
        db=db,
        item_id=item_id,
        client_id=client_id,
    )
