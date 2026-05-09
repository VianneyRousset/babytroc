from typing import Annotated

from fastapi import Depends, Query, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.item import services as item_services
from babytroc.domains.item.schemas.api import ItemMatchinWordsApiQuery
from babytroc.domains.item.schemas.preview import ItemPreviewRead
from babytroc.domains.item.schemas.read import ItemRead
from babytroc.infrastructure.cache import get_cache
from babytroc.infrastructure.cache_client import Cache
from babytroc.infrastructure.database import get_db_session
from babytroc.routers.v1.auth import maybe_client_id_annotation

from .annotations import item_id_annotation
from .router import router


@router.get("", status_code=status.HTTP_200_OK)
async def list_items(
    request: Request,
    response: Response,
    query: Annotated[ItemMatchinWordsApiQuery, Query()],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    cache: Annotated[Cache, Depends(get_cache)],
) -> list[ItemPreviewRead]:
    """List items."""

    # words fuzzy search
    if query.words:
        fuzzy_search_result = await item_services.list_items(
            db=db,
            words=query.words,
            query_filter=query.item_select_query_filter,
            page_options=query.item_matching_words_query_page_options,
            cache=cache,
        )

        fuzzy_search_result.set_response_headers(response, request)

        return fuzzy_search_result.data

    result = await item_services.list_items(
        db=db,
        query_filter=query.item_select_query_filter,
        page_options=query.item_query_page_options,
        cache=cache,
    )

    result.set_response_headers(response, request)

    return result.data


@router.get("/{item_id}", status_code=status.HTTP_200_OK)
async def get_item(
    item_id: item_id_annotation,
    client_id: maybe_client_id_annotation,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    cache: Annotated[Cache, Depends(get_cache)],
) -> ItemRead:
    """Get item."""

    return await item_services.get_item(
        db=db,
        item_id=item_id,
        client_id=client_id,
        cache=cache,
    )
