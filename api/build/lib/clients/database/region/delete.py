from sqlalchemy.orm import Session

from app.models.item import Region


def delete_region(db: Session, region: Region) -> None:
    """Delete the region  from database."""

    db.delete(region)
    db.flush()
