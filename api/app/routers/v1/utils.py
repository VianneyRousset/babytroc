from typing import Annotated, Optional

from fastapi import APIRouter, Query, Request, Response, status

from app import services

router = APIRouter()


@router.get(
    "/avatar",
    responses={
        status.HTTP_200_OK: {
            "content": {
                "image/svg+xml": {},
            },
        }
    },
    response_class=Response,
)
def generate_avatar(
    request: Request,
    size: Annotated[Optional[int], Query(title="Size of the image in pixels.")] = 64,
    seed: Annotated[Optional[str], Query(title="Seed for the avatar generation.")] = 0,
):
    """Generates an avatar based on the given seed."""

    avatar = services.generate_avatar(
        size=size,
        seed=seed,
    )

    return Response(
        content=avatar,
    )
