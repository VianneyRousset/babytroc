from typing import Annotated

from fastapi import Body, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.routers.v1.auth import client_id_annotation
from app.schemas.item.create import ItemCreate
from app.schemas.item.read import ItemRead

from .router import router


@router.post("", status_code=status.HTTP_201_CREATED)
def create_client_item(
    client_id: client_id_annotation,
    item_create: Annotated[
        ItemCreate,
        Body(title="Fields for the item creation."),
    ],
    db: Annotated[Session, Depends(get_db_session)],
) -> ItemRead:
    """Create an item owned by the client."""

    return services.item.create_item(
        db=db,
        owner_id=client_id,
        item_create=item_create,
    )
