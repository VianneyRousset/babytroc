from typing import Annotated

from fastapi import Depends, Request, Response, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.image import services as image_services
from babytroc.domains.image.schemas.read import ItemImageRead
from babytroc.infrastructure.database import get_db_session
from babytroc.routers.v1.auth import client_id_annotation
from babytroc.shared.rate_limit import make_rate_limit_dep

from .router import router

# TODO limite upload size (middleware)


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
    _rate_limited: Annotated[None, Depends(rate_limit_image_upload)],
) -> ItemImageRead:
    """Upload item image."""

    return await image_services.upload_image(
        config=request.app.state.config,
        db=db,
        fp=file.file,
        owner_id=client_id,
    )
