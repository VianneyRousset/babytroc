import io

import requests

from app.config import Config
from app.errors.image import ItemImageNotFoundError
from app.schemas.networking.imgpush import ImgpushUploadResponse

TIMEOUT = 2

# TODO avoid hardcoding image format

# CREATE


def upload_image(config: Config, fp: io.IOBase) -> ImgpushUploadResponse:
    response = requests.post(
        url=config.imgpush.url,
        timeout=TIMEOUT,
        files={"file": ("file.jpg", fp, "image/jpeg")},
    )

    # TODO handler raised exceptions
    response.raise_for_status()

    return ImgpushUploadResponse(**response.json())


# READ


def get_image(config: Config, name: str) -> bytes:
    response = requests.get(
        url=f"{config.imgpush.url}/{name}.jpg",
        timeout=TIMEOUT,
    )

    if response.status_code == 404:
        raise ItemImageNotFoundError({"name": name})

    # TODO better handler other status codes
    response.raise_for_status()

    return response.content
