from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.schemas.region.read import RegionRead

router = APIRouter()


@router.get("/regions", status_code=status.HTTP_200_OK)
def list_regions(
    db: Annotated[Session, Depends(get_db_session)],
) -> list[RegionRead]:
    """List regions."""

    return services.region.list_regions(db)
