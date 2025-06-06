from typing import Annotated

from fastapi import Body, Depends, status
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.routers.v1.auth import client_id_annotation
from app.schemas.item.private import ItemPrivateRead
from app.schemas.item.query import ItemQueryFilter
from app.schemas.item.update import ItemUpdate

from .annotations import item_id_annotation
from .router import router


@router.post("/{item_id}", status_code=status.HTTP_200_OK)
def update_client_item(
    client_id: client_id_annotation,
    item_id: item_id_annotation,
    item_update: Annotated[
        ItemUpdate,
        Body(title="Item fields to update."),
    ],
    db: Annotated[Session, Depends(get_db_session)],
) -> ItemPrivateRead:
    """Update client's item."""

    return services.item.update_item(
        db=db,
        item_id=item_id,
        item_update=item_update,
        query_filter=ItemQueryFilter(
            owner_id=client_id,
        ),
    )
