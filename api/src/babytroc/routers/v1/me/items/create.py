from typing import Annotated

from fastapi import Body, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.item import services as item_services
from babytroc.domains.item.schemas.create import ItemCreate
from babytroc.domains.item.schemas.read import ItemRead
from babytroc.infrastructure.database import get_db_session
from babytroc.routers.v1.auth import client_id_annotation

from .router import router


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_client_item(
    client_id: client_id_annotation,
    item_create: Annotated[
        ItemCreate,
        Body(title="Fields for the item creation."),
    ],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ItemRead:
    """Create an item owned by the client."""

    return await item_services.create_item(
        db=db,
        owner_id=client_id,
        item_create=item_create,
    )
