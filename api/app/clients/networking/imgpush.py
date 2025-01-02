import io

import requests

from app import config
from app.schemas.networking.imgpush import ImgpushUploadResponse

TIMEOUT = 2

# TODO avoid hardcoding image format

# CREATE


def upload_image(fp: io.IOBase) -> ImgpushUploadResponse:
    url = config.IMGPUSH_URL

    response = requests.post(
        url=url,
        timeout=TIMEOUT,
        files={"file": ("file.jpg", fp, "image/jpeg")},
    )

    # TODO handler raised exceptions
    response.raise_for_status()

    return ImgpushUploadResponse(**response.json())


# READ


def get_image(name: str) -> bytes:
    url = f"{config.IMGPUSH_URL}/{name}.jpg"
    response = requests.get(
        url=url,
        timeout=TIMEOUT,
    )

    # TODO handler raised exceptions
    response.raise_for_status()

    return response.content
