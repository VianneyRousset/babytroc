from typing import Annotated

from fastapi import Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.item import services as item_services
from app.infrastructure.cache import get_cache
from app.infrastructure.cache_client import Cache
from app.infrastructure.database import get_db_session
from app.routers.v1.auth import client_id_annotation
from app.domains.item.schemas.query import ItemDeleteQueryFilter

from .annotations import item_id_annotation
from .router import router


@router.delete("/{item_id}", status_code=status.HTTP_200_OK)
async def delete_client_item(
    client_id: client_id_annotation,
    item_id: item_id_annotation,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    cache: Annotated[Cache, Depends(get_cache)],
):
    """Delete the specified item owned by the client."""

    return await item_services.delete_item(
        db=db,
        item_id=item_id,
        query_filter=ItemDeleteQueryFilter(
            owner_id=client_id,
        ),
        cache=cache,
    )
