from typing import Annotated

from fastapi import Body, Request, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.schemas.item.private import ItemPrivateRead
from app.schemas.item.query import ItemQueryFilter
from app.schemas.item.update import ItemUpdate

from .annotations import item_id_annotation
from .router import router


@router.post("/{item_id}", status_code=status.HTTP_200_OK)
def update_client_item(
    request: Request,
    item_id: item_id_annotation,
    item_update: Annotated[
        ItemUpdate,
        Body(title="Item fields to update."),
    ],
    db: Annotated[Session, Depends(get_db_session)],
) -> ItemPrivateRead:
    """Update client's item."""

    client_user_id = services.auth.check_auth(request)

    return services.item.update_item(
        db=db,
        item_id=item_id,
        item_update=item_update,
        query_filter=ItemQueryFilter(
            owner_id=client_user_id,
        ),
    )
