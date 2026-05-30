import asyncio
from typing import Annotated

from fastapi import Depends, Request, Response, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.image import services as image_services
from babytroc.domains.image.errors import ImageTooLargeError
from babytroc.domains.image.schemas.read import ItemImageRead
from babytroc.infrastructure.database import get_db_session
from babytroc.infrastructure.image_processing import get_image_processing_semaphore
from babytroc.routers.v1.auth import client_id_annotation
from babytroc.shared.rate_limit import make_rate_limit_dep

from .router import router

rate_limit_image_upload = make_rate_limit_dep(
    key_prefix="image_upload",
    extract_config=lambda c: c.image_upload,
)


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_image(
    client_id: client_id_annotation,
    request: Request,
    response: Response,
    file: UploadFile,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    semaphore: Annotated[asyncio.Semaphore, Depends(get_image_processing_semaphore)],
    _rate_limited: Annotated[None, Depends(rate_limit_image_upload)],
) -> ItemImageRead:
    """Upload item image."""

    config = request.app.state.config
    max_bytes = config.image.max_upload_bytes

    data = await file.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ImageTooLargeError(actual=len(data), limit=max_bytes)

    return await image_services.upload_image(
        config=config,
        db=db,
        semaphore=semaphore,
        owner_id=client_id,
        data=data,
    )
