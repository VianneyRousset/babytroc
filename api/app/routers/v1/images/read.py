from typing import Annotated

from fastapi import Path, Query, Request, Response, status

from app import services
from app.schemas.image.query import ItemImageQuery

from .router import router


@router.get("/{image_name}", status_code=status.HTTP_200_OK)
def get_item_image(
    request: Request,
    image_name: Annotated[str, Path()],
    query: Annotated[ItemImageQuery, Query()],
) -> Response:
    """Get item image."""

    image = services.image.get_image_data(
        config=request.app.state.config,
        image_name=image_name,
        size=query.size,
    )

    return Response(
        content=image,
        media_type="image/jpeg",
    )
