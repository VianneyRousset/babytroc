from typing import Annotated

from fastapi import Path, Request, Response, status

from app import services

from .router import router


@router.get("/{image_name}", status_code=status.HTTP_200_OK)
def get_item_image(
    request: Request,
    image_name: Annotated[str, Path()],
) -> Response:
    """Get item image."""

    services.auth.check_auth(request)

    image = services.image.get_image_data(request.app.state.config, image_name)

    return Response(
        content=image,
        media_type="image/jpeg",
    )
