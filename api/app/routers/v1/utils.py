from typing import Annotated, Optional

from fastapi import APIRouter, Path, Query, Request, Response, status

from app import services

router = APIRouter()


@router.get(
    "/avatars/{seed}",
    responses={
        status.HTTP_200_OK: {
            "content": {
                "image/svg+xml": {},
            },
        }
    },
    response_class=Response,
)
def get_avatar(
    request: Request,
    seed: Annotated[Optional[str], Path(title="Seed for the avatar generation.")],
    size: Annotated[Optional[int], Query(title="Size of the image in pixels.")] = 64,
):
    """Generates an avatar based on the given seed."""

    avatar = services.avatar.get_avatar(
        size=size,
        seed=seed,
    )

    return Response(
        content=avatar,
        media_type="image/svg+xml",
    )
