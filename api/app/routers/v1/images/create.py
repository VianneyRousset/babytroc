from fastapi import Depends, Request, Response, UploadFile
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.schemas.image.read import ItemImageRead

from .router import router

# TODO limite upload size (middleware)


@router.post("")
async def upload_image(
    request: Request,
    response: Response,
    file: UploadFile,
    db: Session = Depends(get_db_session),
) -> ItemImageRead:
    """Upload item image."""

    client_user_id = services.auth.check_auth(request)

    return services.image.upload_image(
        config=request.app.state.config,
        db=db,
        fp=file.file,
        owner_id=client_user_id,
    )
