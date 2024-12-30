from typing import Annotated

from fastapi import Body, Request, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.schemas.item.create import ItemCreate
from app.schemas.item.preview import ItemPreviewRead

from .router import router


@router.post("", status_code=status.HTTP_201_CREATED)
def create_client_item(
    request: Request,
    item_create: Annotated[
        ItemCreate,
        Body(title="Fields for the item creation."),
    ],
    db: Session = Depends(get_db_session),
) -> ItemPreviewRead:
    """Create an item owned by the client."""

    client_user_id = services.auth.check_auth(request)

    return services.item.create_item(
        db=db,
        owner_id=client_user_id,
        item_create=item_create,
    )
