from typing import Annotated

from fastapi import Depends, status
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.routers.v1.auth import client_id_annotation
from app.schemas.item.query import ItemDeleteQueryFilter

from .annotations import item_id_annotation
from .router import router


@router.delete("/{item_id}", status_code=status.HTTP_200_OK)
def delete_client_item(
    client_id: client_id_annotation,
    item_id: item_id_annotation,
    db: Annotated[Session, Depends(get_db_session)],
):
    """Delete the specified item owned by the client."""

    return services.item.delete_item(
        db=db,
        item_id=item_id,
        query_filter=ItemDeleteQueryFilter(
            owner_id=client_id,
        ),
    )
