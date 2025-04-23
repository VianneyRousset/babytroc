from typing import Annotated

from fastapi import Depends, Request, Response, UploadFile, status
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.routers.v1.auth import client_id_annotation
from app.schemas.image.read import ItemImageRead

from .router import router

# TODO limite upload size (middleware)


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_image(
    client_id: client_id_annotation,
    request: Request,
    response: Response,
    file: UploadFile,
    db: Annotated[Session, Depends(get_db_session)],
) -> ItemImageRead:
    """Upload item image."""

    return services.image.upload_image(
        config=request.app.state.config,
        db=db,
        fp=file.file,
        owner_id=client_id,
    )
