from typing import Annotated

from fastapi import Body, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import services
from app.database import get_db_session
from app.routers.v1.auth import client_id_annotation
from app.schemas.item.query import ItemUpdateQueryFilter
from app.schemas.item.read import ItemRead
from app.schemas.item.update import ItemUpdate

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
) -> ItemRead:
    """Update client's item."""

    return await services.item.update_item(
        db=db,
        item_id=item_id,
        item_update=item_update,
        query_filter=ItemUpdateQueryFilter(
            owner_id=client_id,
        ),
    )
