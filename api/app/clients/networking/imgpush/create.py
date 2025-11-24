import asyncio
import io

import aiohttp

from app.config import Config
from app.schemas.networking.imgpush import ImgpushUploadResponse

from .constants import TIMEOUT


async def upload_image(
    config: Config,
    image: io.IOBase,
) -> ImgpushUploadResponse:
    """Upload given image `fp` to imgpush."""

    responses = await upload_many_images(
        config=config,
        images=[image],
    )

    return responses[0]


async def upload_many_images(
    config: Config,
    images: list[io.IOBase],
) -> list[ImgpushUploadResponse]:
    """Upload all given images `fps` to imgpush."""

    async with aiohttp.ClientSession() as session:
        responses = await asyncio.gather(
            *(
                _post_image_to_imgpush(
                    session=session,
                    url=config.imgpush.url,
                    fp=image,
                )
                for image in images
            )
        )

    return [ImgpushUploadResponse(**resp) for resp in responses]


async def _post_image_to_imgpush(
    session: aiohttp.ClientSession,
    url: str,
    fp: io.IOBase,
) -> dict:
    async with session.post(url, timeout=TIMEOUT) as response:
        return await response.json()
