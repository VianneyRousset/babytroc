from fastapi import Request, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session

from .annotations import item_id_annotation
from .router import router


@router.delete("/item_id}", status_code=status.HTTP_200_OK)
def delete_client_item(
    request: Request,
    item_id: item_id_annotation,
    db: Session = Depends(get_db_session),
):
    """Delete the specified item owned by the client."""

    client_user_id = services.auth.check_auth(request)

    return services.items.delete_user_item(
        db=db,
        user_id=client_user_id,
        item_id=item_id,
    )
