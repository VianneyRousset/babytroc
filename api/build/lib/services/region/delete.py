from sqlalchemy.orm import Session

from app.clients import database


def delete_region(
    db: Session,
    region_id: int,
) -> None:
    """Delete region with `region_id`."""

    # get region
    region = database.region.get_region(
        db=db,
        region_id=region_id,
    )

    # delete region
    database.region.delete_region(
        db=db,
        region=region,
    )
