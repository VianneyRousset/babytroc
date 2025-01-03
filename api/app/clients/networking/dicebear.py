import requests

URL = "https://api.dicebear.com/7.x/thumbs/svg"
TIMEOUT = 2

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
    response = requests.get(
        url=URL,
        params={
            "seed": seed,
            "size": size,
            "scale": scale,
            "radius": radius,
            "backgroundColor": bg,
            "shapeColor": fg,
        },
        timeout=TIMEOUT,
    )

    # TODO handler raised exceptions
    response.raise_for_status()

    return response.content
