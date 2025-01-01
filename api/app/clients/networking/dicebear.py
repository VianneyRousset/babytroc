import requests

from app import config

# READ


def generate_avatar(
    seed: str,
    *,
    size: int,
    scale: int,
    radius: int,
    bg: str,
    fg: str,
) -> bytes:
    url = config.DICEBEAR_URL

    response = requests.get(
        url=url,
        params={
            "seed": seed,
            "size": size,
            "scale": scale,
            "radius": radius,
            "backgroundColor": bg,
            "shapeColor": fg,
        },
        timeout=config.IMGPUSH_TIMEOUT,
    )

    # TODO handler raised exceptions
    response.raise_for_status()

    return response.content
