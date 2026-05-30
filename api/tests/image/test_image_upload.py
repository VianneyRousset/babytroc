import io
import struct
import zlib
from http import HTTPStatus

import PIL.Image
from httpx import AsyncClient

from babytroc.infrastructure.config import Config


def _png_bytes(width: int, height: int) -> bytes:
    img = PIL.Image.new("RGB", (width, height), color="red")
    fp = io.BytesIO()
    img.save(fp, format="PNG")
    return fp.getvalue()


def _bomb_png(width: int, height: int) -> bytes:
    """Minimal PNG whose IHDR declares huge dimensions (no real pixel data)."""
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr_body = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    ihdr_crc = zlib.crc32(b"IHDR" + ihdr_body)
    ihdr = struct.pack(">I", 13) + b"IHDR" + ihdr_body + struct.pack(">I", ihdr_crc)
    iend_crc = zlib.crc32(b"IEND")
    iend = struct.pack(">I", 0) + b"IEND" + struct.pack(">I", iend_crc)
    return sig + ihdr + iend


async def test_upload_image_happy_path_returns_201(alice_client: AsyncClient):
    data = _png_bytes(300, 200)
    response = await alice_client.post(
        "/api/v1/images",
        files={"file": ("ok.png", io.BytesIO(data), "image/png")},
    )
    assert response.status_code == HTTPStatus.CREATED, response.text
    body = response.json()
    assert body["name"]


async def test_upload_image_oversized_returns_413(
    alice_client: AsyncClient,
    app_config: Config,
):
    too_big = b"x" * (app_config.image.max_upload_bytes + 1)
    response = await alice_client.post(
        "/api/v1/images",
        files={"file": ("big.bin", io.BytesIO(too_big), "application/octet-stream")},
    )
    assert response.status_code == HTTPStatus.REQUEST_ENTITY_TOO_LARGE, response.text


async def test_upload_image_decompression_bomb_returns_400(
    alice_client: AsyncClient,
):
    bomb = _bomb_png(20_000, 20_000)
    response = await alice_client.post(
        "/api/v1/images",
        files={"file": ("bomb.png", io.BytesIO(bomb), "image/png")},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.text


async def test_upload_image_invalid_bytes_returns_400(alice_client: AsyncClient):
    response = await alice_client.post(
        "/api/v1/images",
        files={
            "file": (
                "garbage.bin",
                io.BytesIO(b"definitely not an image"),
                "application/octet-stream",
            ),
        },
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.text
