# Async-Correct Image Upload with Memory Safety

Fix the `async`/sync mismatch in `upload_image`, stop blocking the event loop on PIL work, and add three layered memory-safety guards (upload size, decompression bomb, concurrency).

## Context

`domains/image/services/create.py::upload_image` is declared `async def` but takes `fp: IO[bytes]` (a sync file-like). Inside it, `image_utils.generate_webp_variants(fp)` runs PIL decode + EXIF normalization + resize + WebP encode — all CPU-bound and blocking the event loop on every upload. The S3 upload at the end is genuinely async via `aioboto3`.

Two concrete problems:

1. **Type/contract lie.** The router happens to pass a sync `SpooledTemporaryFile` (`UploadFile.file`), which works. The seed script (`babycli/seed/items.py`) passes a `trio.Path` async file handle — typed as `IO[bytes]` but with async `.read()`. PIL calling `.read()` on it returns a coroutine, not bytes. The seed path would fail or rely on accidents.
2. **Event-loop blocking.** PIL is fully synchronous. A 4 MP decode + WebP encode takes hundreds of ms on a typical server CPU. While that runs, no other request progresses on this worker.

There is no async-native image library worth adopting (Pillow, Pillow-SIMD, pyvips, wand, opencv are all sync). The idiomatic fix is to offload PIL work to a thread via `asyncio.to_thread(...)`. PIL releases the GIL during its C-level decode/encode operations, so threaded calls yield real parallelism.

Also, the router has a long-standing `# TODO limite upload size (middleware)` comment with no enforcement. A user can today upload an arbitrarily large file or a decompression bomb and OOM the worker.

## Requirements

- `upload_image` service is fully async-correct: no sync IO objects in the signature, no event-loop blocking.
- Three independent memory-safety guards, each configurable:
  - **Upload byte cap** at the router boundary.
  - **Decompression bomb cap** at the PIL layer.
  - **Concurrent image processing cap** per worker.
- Configurable via env vars with sensible defaults: 5 MB / 16 MP / 4-per-worker.
- Typed `ApiError` subclasses for each rejection path (413 / 400) — no leaking raw PIL exceptions as 500s.
- Seed script (`babycli/seed/items.py`) uses the same service path with no special-casing.
- Service layer remains framework-agnostic (no `UploadFile` in service signatures).

## Architecture

```
Request → Router (read with byte cap, 413 if over)
        → Service (acquire per-worker semaphore)
            → asyncio.to_thread(generate_webp_variants, BytesIO(data))
                PIL: open → verify → MAX_IMAGE_PIXELS check → resize → encode
            → release semaphore
        → S3 upload (already async)
        → DB insert
```

**Layering preserved.** Service knows nothing about FastAPI. Router enforces the network-edge byte cap. Config wires the limits. Seed uses the same service, constructing its own semaphore.

## Config

New `ImageConfig` in `infrastructure/config.py`:

```python
class ImageConfig(NamedTuple):
    max_upload_bytes: int                       # IMAGE_MAX_UPLOAD_BYTES
    max_pixels: int                             # IMAGE_MAX_PIXELS
    max_concurrent_processing_per_worker: int   # IMAGE_MAX_CONCURRENT_PROCESSING_PER_WORKER

    @classmethod
    def from_env(cls, *, test: bool | None = None) -> Self:
        env = EnvironmentVariablesReader(test=test)
        return cls(
            max_upload_bytes=int(env.get(
                "IMAGE_MAX_UPLOAD_BYTES",
                default=str(5 * 1024 * 1024),
            )),
            max_pixels=int(env.get(
                "IMAGE_MAX_PIXELS",
                default="16000000",
            )),
            max_concurrent_processing_per_worker=int(env.get(
                "IMAGE_MAX_CONCURRENT_PROCESSING_PER_WORKER",
                default="4",
            )),
        )
```

Added as `image: ImageConfig` on the top-level `Config`, constructed in `Config.from_env()` next to the existing nested configs.

**Important note on per-worker semantics:** the concurrency cap is per uvicorn worker process. With `WORKERS × IMAGE_MAX_CONCURRENT_PROCESSING_PER_WORKER × per-image-memory`, you get peak image-processing memory. With defaults (e.g. 4 workers × 4 concurrent × ~64 MB peak per 16 MP RGBA image) ≈ 1 GB process-image budget. Tune to fit deployment.

## Lifecycle wiring

New `infrastructure/image_processing.py` mirrors the existing infrastructure dependency pattern (compare `infrastructure/cache.py`, `infrastructure/database.py`, `infrastructure/email.py`, `infrastructure/pubsub.py`):

```python
import asyncio

_image_processing_semaphore: asyncio.Semaphore


def init_image_processing_dependency(semaphore: asyncio.Semaphore) -> None:
    global _image_processing_semaphore
    _image_processing_semaphore = semaphore


def get_image_processing_semaphore() -> asyncio.Semaphore:
    return _image_processing_semaphore
```

In `app.py::create_app()`:

```python
from babytroc.infrastructure.image_processing import init_image_processing_dependency
from babytroc.shared.image import configure_pillow_pixel_limit

# ... existing setup ...

# Image processing setup
configure_pillow_pixel_limit(config.image.max_pixels)
image_processing_semaphore = asyncio.Semaphore(
    config.image.max_concurrent_processing_per_worker
)
init_image_processing_dependency(image_processing_semaphore)
```

`asyncio.Semaphore()` in Python 3.10+ does not bind to a loop at construction; it binds on first `acquire()`. Safe to create in the sync `create_app()`.

The semaphore is not stashed on `app.state` because no middleware/websocket consumer needs it — only the image router uses it, and it gets there via `Depends(get_image_processing_semaphore)`.

Babycli setup paths that don't go through `create_app()` (seed) call `configure_pillow_pixel_limit(config.image.max_pixels)` at their own startup and construct their own `asyncio.Semaphore(...)` from the same `config.image` namespace. They pass the semaphore to the service directly rather than going through `init_image_processing_dependency`, since they don't use FastAPI's dependency machinery.

## Service rewrite

`domains/image/services/create.py`:

```python
import asyncio
import uuid
from io import BytesIO

import PIL.Image
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.image.errors import (
    ImagePixelLimitError,
    ImageTooLargeError,
    InvalidImageError,
)
from babytroc.domains.image.schemas.read import ItemImageRead
from babytroc.domains.item.models.image import ItemImage
from babytroc.domains.user.services.read import get_user
from babytroc.infrastructure import storage
from babytroc.infrastructure.config import Config
from babytroc.shared import image as image_utils


async def upload_image(
    config: Config,
    db: AsyncSession,
    semaphore: asyncio.Semaphore,
    *,
    owner_id: int,
    data: bytes,
) -> ItemImageRead:
    """Upload a new item image. Generates webp variants and stores in S3."""

    if len(data) > config.image.max_upload_bytes:
        raise ImageTooLargeError(
            actual=len(data),
            limit=config.image.max_upload_bytes,
        )

    async with semaphore:
        try:
            variants = await asyncio.to_thread(
                image_utils.generate_webp_variants,
                BytesIO(data),
            )
        except PIL.Image.DecompressionBombError as error:
            raise ImagePixelLimitError(config.image.max_pixels) from error
        except (PIL.UnidentifiedImageError, OSError, SyntaxError) as error:
            raise InvalidImageError() from error

    name = uuid.uuid4().hex

    await storage.upload_image_variants(
        config=config.s3,
        name=name,
        variants=variants,
    )

    stmt = (
        insert(ItemImage)
        .values({"name": name, "owner_id": owner_id})
        .returning(ItemImage)
    )

    try:
        res = await db.execute(stmt)
        item_image = res.unique().scalars().one()
    except IntegrityError as error:
        await get_user(db=db, user_id=owner_id)
        raise error

    return ItemImageRead.model_validate(item_image)
```

**Defense-in-depth byte cap.** The service re-checks `len(data)` even though the router enforces it. The seed script and any future internal caller bypassing the router still get protected.

**Exception translation.** PIL raises `OSError`, `SyntaxError`, or `UnidentifiedImageError` for malformed image bytes. All three become `InvalidImageError` (400). `DecompressionBombError` becomes `ImagePixelLimitError` (400). No raw PIL exceptions surface to clients as 500s.

## Image utils (`shared/image.py`)

Add a small helper, no signature changes to `generate_webp_variants`:

```python
def configure_pillow_pixel_limit(max_pixels: int) -> None:
    """Set PIL's decompression-bomb cap (module-global PIL state)."""
    PIL.Image.MAX_IMAGE_PIXELS = max_pixels
```

PIL enforces `MAX_IMAGE_PIXELS` during `Image.open()` based on declared dimensions in the header — bombs are rejected before full decode, bounding peak memory.

`generate_webp_variants` itself is unchanged in shape, but its input is now always `BytesIO` (built by the service from `bytes`). The function still takes `IO[bytes]` since `BytesIO` satisfies it; this is now an internal contract, not crossing the async boundary.

## Router (`routers/v1/images/create.py`)

```python
import asyncio
from typing import Annotated

from fastapi import Depends, Request, Response, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.image import services as image_services
from babytroc.domains.image.errors import ImageTooLargeError
from babytroc.domains.image.schemas.read import ItemImageRead
from babytroc.infrastructure.database import get_db_session
from babytroc.infrastructure.image_processing import get_image_processing_semaphore
from babytroc.routers.v1.auth import client_id_annotation
from babytroc.shared.rate_limit import make_rate_limit_dep

from .router import router


rate_limit_image_upload = make_rate_limit_dep(
    key_prefix="image_upload",
    extract_config=lambda c: c.image_upload,
)


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_image(
    client_id: client_id_annotation,
    request: Request,
    response: Response,
    file: UploadFile,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    semaphore: Annotated[asyncio.Semaphore, Depends(get_image_processing_semaphore)],
    _rate_limited: Annotated[None, Depends(rate_limit_image_upload)],
) -> ItemImageRead:
    """Upload item image."""

    config = request.app.state.config
    max_bytes = config.image.max_upload_bytes

    data = await file.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ImageTooLargeError(actual=len(data), limit=max_bytes)

    return await image_services.upload_image(
        config=config,
        db=db,
        semaphore=semaphore,
        owner_id=client_id,
        data=data,
    )
```

`await file.read(max_bytes + 1)` caps how many bytes we buffer — the +1 distinguishes "at-limit" from "over-limit" without pulling more than necessary. The router's byte check is the primary boundary; the service re-check is defense in depth.

The `get_image_processing_semaphore` dependency is the one defined in `infrastructure/image_processing.py` (see Lifecycle wiring).

The router-level `# TODO limite upload size (middleware)` comment is removed.

## Errors (`domains/image/errors.py`)

```python
from http import HTTPStatus

from babytroc.shared.errors import ApiError, BadRequestError, ConflictError, NotFoundError


class ItemImageError(ApiError):
    """Exception related to an item image."""


class ImageTooLargeError(ItemImageError):
    def __init__(self, actual: int, limit: int):
        super().__init__(
            f"Image too large: {actual} bytes (max {limit})",
            status_code=HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
        )


class ImagePixelLimitError(ItemImageError, BadRequestError):
    def __init__(self, max_pixels: int):
        super().__init__(f"Image exceeds max pixel count of {max_pixels}")


class InvalidImageError(ItemImageError, BadRequestError):
    def __init__(self):
        super().__init__("Invalid or unreadable image file")


# (existing ItemImageNotFoundError, ItemImageNotOwnedError unchanged)
```

## Seed script (`babycli/seed/items.py`)

```python
async def upload_image(
    db: AsyncSession,
    config: Config,
    semaphore: asyncio.Semaphore,
    fp: Path,
    owner_id: int,
) -> str:
    """Upload image."""

    data = await fp.read_bytes()
    image = await _upload_image(
        config=config,
        db=db,
        semaphore=semaphore,
        owner_id=owner_id,
        data=data,
    )
    return image.name
```

The seed caller creates the semaphore once and threads it through:

```python
configure_pillow_pixel_limit(config.image.max_pixels)
semaphore = asyncio.Semaphore(config.image.max_concurrent_processing_per_worker)
```

If seed images themselves exceed the limits, the seed fails loudly — that's correct behavior, not a special case to bypass.

## Testing

Test cases to add (in `tests/image/`):

- **Regression**: existing happy-path upload still produces an `ItemImageRead` and the expected webp variants.
- **413 oversized upload**: POST a payload > `max_upload_bytes` → `ImageTooLargeError` → response 413.
- **400 decompression bomb**: PNG header declaring dimensions > `max_pixels` → `ImagePixelLimitError` → response 400.
- **400 invalid bytes**: random/non-image bytes → `InvalidImageError` → response 400.
- **Event-loop responsiveness**: while a large upload is in flight, a concurrent lightweight request (`GET /`) returns within a tight bound (e.g., < 50 ms). Asserts the loop is not blocked.
- **Semaphore bound**: monkeypatch `generate_webp_variants` with a sleep; fire `N > limit` parallel uploads; assert peak concurrent in-flight ≤ limit.

Test config: `TEST_IMAGE_MAX_CONCURRENT_PROCESSING_PER_WORKER=2` (and similar `TEST_` overrides for the other knobs) via the existing test-env mechanism — keeps test runs predictable and avoids accidental coupling to production defaults.

## Out of scope

- Replacing PIL with pyvips / Pillow-SIMD for speed/memory wins. Separate decision, orthogonal to async-correctness.
- Streaming uploads / chunked decode. PIL needs the full image in memory; with the byte cap, the buffered-`bytes` design is correct.
- Global content-length middleware. The per-route `await file.read(max + 1)` is enough for now; a middleware would be a defense-in-depth duplication worth considering later if more upload endpoints appear.
- Process-pool offload (`ProcessPoolExecutor`) for true CPU parallelism past GIL. Threads + GIL-releasing PIL operations are sufficient at expected scale.
