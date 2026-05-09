from typing import Annotated

from fastapi import Depends, Request, Response, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.image import services as image_services
from app.domains.image.schemas.read import ItemImageRead
from app.infrastructure.database import get_db_session
from app.routers.v1.auth import client_id_annotation

from .router import router

# TODO limite upload size (middleware)


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_image(
    client_id: client_id_annotation,
    request: Request,
    response: Response,
    file: UploadFile,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ItemImageRead:
    """Upload item image."""

    return await image_services.upload_image(
        config=request.app.state.config,
        db=db,
        fp=file.file,
        owner_id=client_id,
    )
