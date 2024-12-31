import io

import requests

from app import config
from app.schemas.networking.imgpush import ImgpushUploadResponse


def upload_image(fp: io.IOBase) -> ImgpushUploadResponse:
    url = config.IMGPUSH_URL
    fp.seek(0)
    response = requests.post(
        url=url,
        timeout=config.IMGPUSH_TIMEOUT,
        files={"file": ("file.jpg", fp, "image/jpeg")},
    )
    response.raise_for_status()
    return ImgpushUploadResponse(**response.json())
