from typing import Annotated

from fastapi import Body, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.item import services as item_services
from app.infrastructure.cache import get_cache
from app.infrastructure.cache_client import Cache
from app.infrastructure.database import get_db_session
from app.routers.v1.auth import client_id_annotation
from app.domains.item.schemas.query import ItemUpdateQueryFilter
from app.domains.item.schemas.read import ItemRead
from app.domains.item.schemas.update import ItemUpdate

from .annotations import item_id_annotation
from .router import router


@router.post("/{item_id}", status_code=status.HTTP_200_OK)
async def update_client_item(
    client_id: client_id_annotation,
    item_id: item_id_annotation,
    item_update: Annotated[
        ItemUpdate,
        Body(title="Item fields to update."),
    ],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    cache: Annotated[Cache, Depends(get_cache)],
) -> ItemRead:
    """Update client's item."""

    return await item_services.update_item(
        db=db,
        item_id=item_id,
        item_update=item_update,
        query_filter=ItemUpdateQueryFilter(
            owner_id=client_id,
        ),
        cache=cache,
    )
