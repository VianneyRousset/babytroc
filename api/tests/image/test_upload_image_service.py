import asyncio
import struct
import zlib
from io import BytesIO

import PIL.Image
import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from babytroc.domains.image.errors import (
    ImagePixelLimitError,
    ImageTooLargeError,
    InvalidImageError,
)
from babytroc.domains.image.services.create import upload_image
from babytroc.domains.user.schemas.private import UserPrivateRead
from babytroc.infrastructure.config import Config
from babytroc.shared.image import configure_pillow_pixel_limit


def _png_bytes(width: int, height: int) -> bytes:
    img = PIL.Image.new("RGB", (width, height), color="red")
    fp = BytesIO()
    img.save(fp, format="PNG")
    return fp.getvalue()


def _crafted_png_header_with_dimensions(width: int, height: int) -> bytes:
    """Return a minimal PNG header declaring `width` x `height`.

    PIL inspects the IHDR chunk during `open()` and raises
    `DecompressionBombError` if width*height > MAX_IMAGE_PIXELS, without
    decoding the full image.
    """
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr_body = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    ihdr_crc = zlib.crc32(b"IHDR" + ihdr_body)
    ihdr = struct.pack(">I", 13) + b"IHDR" + ihdr_body + struct.pack(">I", ihdr_crc)
    iend_crc = zlib.crc32(b"IEND")
    iend = struct.pack(">I", 0) + b"IEND" + struct.pack(">I", iend_crc)
    return sig + ihdr + iend


@pytest.fixture
def small_semaphore() -> asyncio.Semaphore:
    return asyncio.Semaphore(4)


async def test_upload_image_happy_path_returns_image_read(
    app_config: Config,
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
    small_semaphore: asyncio.Semaphore,
):
    data = _png_bytes(200, 100)
    async with database_sessionmaker.begin() as session:
        result = await upload_image(
            config=app_config,
            db=session,
            semaphore=small_semaphore,
            owner_id=alice.id,
            data=data,
        )

    assert result.name
    assert result.owner_id == alice.id


async def test_upload_image_rejects_oversized_bytes(
    app_config: Config,
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
    small_semaphore: asyncio.Semaphore,
):
    too_big = b"x" * (app_config.image.max_upload_bytes + 1)
    async with database_sessionmaker.begin() as session:
        with pytest.raises(ImageTooLargeError):
            await upload_image(
                config=app_config,
                db=session,
                semaphore=small_semaphore,
                owner_id=alice.id,
                data=too_big,
            )


async def test_upload_image_rejects_decompression_bomb(
    app_config: Config,
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
    small_semaphore: asyncio.Semaphore,
):
    original_limit = PIL.Image.MAX_IMAGE_PIXELS
    try:
        configure_pillow_pixel_limit(app_config.image.max_pixels)
        bomb = _crafted_png_header_with_dimensions(20_000, 20_000)  # 400 MP
        async with database_sessionmaker.begin() as session:
            with pytest.raises(ImagePixelLimitError):
                await upload_image(
                    config=app_config,
                    db=session,
                    semaphore=small_semaphore,
                    owner_id=alice.id,
                    data=bomb,
                )
    finally:
        PIL.Image.MAX_IMAGE_PIXELS = original_limit


async def test_upload_image_rejects_invalid_bytes(
    app_config: Config,
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
    small_semaphore: asyncio.Semaphore,
):
    async with database_sessionmaker.begin() as session:
        with pytest.raises(InvalidImageError):
            await upload_image(
                config=app_config,
                db=session,
                semaphore=small_semaphore,
                owner_id=alice.id,
                data=b"definitely not an image",
            )
