from typing import Annotated

from fastapi import Body, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.item import services as item_services
from app.domains.item.schemas.create import ItemCreate
from app.domains.item.schemas.read import ItemRead
from app.infrastructure.cache import get_cache
from app.infrastructure.cache_client import Cache
from app.infrastructure.database import get_db_session
from app.routers.v1.auth import client_id_annotation

from .router import router


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_client_item(
    client_id: client_id_annotation,
    item_create: Annotated[
        ItemCreate,
        Body(title="Fields for the item creation."),
    ],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    cache: Annotated[Cache, Depends(get_cache)],
) -> ItemRead:
    """Create an item owned by the client."""

    return await item_services.create_item(
        db=db,
        owner_id=client_id,
        item_create=item_create,
        cache=cache,
    )
