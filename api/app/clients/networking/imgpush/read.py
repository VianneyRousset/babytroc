import io

import aiohttp
from fastapi import status

from app.config import Config
from app.errors.image import ItemImageNotFoundError

from .constants import TIMEOUT

# TODO avoid hardcoding image format


async def _post_image_to_imgpush(
    session: aiohttp.ClientSession,
    url: str,
    fp: io.IOBase,
) -> dict:
    async with session.get(url, timeout=TIMEOUT) as response:
        return await response.json()


async def get_image(
    config: Config,
    name: str,
    *,
    size: int | None = None,
) -> bytes:
    url = (
        f"{config.imgpush.url}/{name}.jpg?w={size}"
        if size
        else f"{config.imgpush.url}/{name}.jpg"
    )

    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=TIMEOUT) as response:
            if response.status == status.HTTP_404_NOT_FOUND:
                raise ItemImageNotFoundError({"name": name})

            # TODO better handler other status codes
            response.raise_for_status()

            return await response.content.read()
