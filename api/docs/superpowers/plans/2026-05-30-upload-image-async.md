# Async-Correct Image Upload — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `upload_image` service fully async-correct (PIL offloaded to a thread) and add three layered memory-safety guards: upload byte cap (5 MB default), decompression-bomb pixel cap (16 MP default), per-worker concurrency cap (4 default).

**Architecture:** Service takes `bytes` instead of sync IO; PIL work runs via `asyncio.to_thread` under an `asyncio.Semaphore` from a new `infrastructure/image_processing` module; router enforces upload size at the network edge; PIL's `MAX_IMAGE_PIXELS` is set at app/CLI startup to reject decompression bombs early; typed `ApiError` subclasses replace raw PIL exceptions in API responses.

**Tech Stack:** FastAPI, Pillow, SQLAlchemy async, pytest-asyncio.

**Spec:** `docs/superpowers/specs/2026-05-30-upload-image-async-design.md`

---

## File Map

**Create:**
- `src/babytroc/infrastructure/image_processing.py` — semaphore init/get dependency
- `tests/test_image_config.py` — ImageConfig unit tests
- `tests/test_image_errors.py` — new error classes unit tests
- `tests/test_image_processing_dep.py` — image_processing dep unit tests
- `tests/image/test_upload_image_service.py` — service unit tests
- `tests/image/test_image_upload.py` — HTTP integration tests for upload boundaries
- `tests/image/test_image_upload_concurrency.py` — semaphore + event-loop tests

**Modify:**
- `src/babytroc/infrastructure/config.py` — add `ImageConfig` and wire it into `Config`
- `src/babytroc/shared/image.py` — add `configure_pillow_pixel_limit`
- `src/babytroc/domains/image/errors.py` — add three error classes
- `src/babytroc/domains/image/services/create.py` — rewrite `upload_image`
- `src/babytroc/app.py` — call `configure_pillow_pixel_limit` and init semaphore
- `src/babytroc/routers/v1/images/create.py` — enforce upload byte cap, new service call
- `src/babycli/seed/items.py` — read bytes, thread semaphore, set PIL pixel limit
- `tests/test_image_variants.py` — add a test for the new helper

---

### Task 1: Add `ImageConfig` to `infrastructure/config.py`

**Files:**
- Create: `tests/test_image_config.py`
- Modify: `src/babytroc/infrastructure/config.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_image_config.py`:

```python
import pytest

from babytroc.infrastructure.config import Config, ImageConfig

IMAGE_ENV_VARS = (
    "IMAGE_MAX_UPLOAD_BYTES",
    "IMAGE_MAX_PIXELS",
    "IMAGE_MAX_CONCURRENT_PROCESSING_PER_WORKER",
)


@pytest.fixture
def _clear_image_env(monkeypatch: pytest.MonkeyPatch):
    for k in IMAGE_ENV_VARS:
        monkeypatch.delenv(k, raising=False)
        monkeypatch.delenv(f"TEST_{k}", raising=False)


def test_image_config_defaults(_clear_image_env):
    config = ImageConfig.from_env(test=False)
    assert config.max_upload_bytes == 5 * 1024 * 1024
    assert config.max_pixels == 16_000_000
    assert config.max_concurrent_processing_per_worker == 4


def test_image_config_env_overrides(
    _clear_image_env,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("IMAGE_MAX_UPLOAD_BYTES", "10485760")
    monkeypatch.setenv("IMAGE_MAX_PIXELS", "8000000")
    monkeypatch.setenv("IMAGE_MAX_CONCURRENT_PROCESSING_PER_WORKER", "8")

    config = ImageConfig.from_env(test=False)

    assert config.max_upload_bytes == 10_485_760
    assert config.max_pixels == 8_000_000
    assert config.max_concurrent_processing_per_worker == 8


def test_image_config_is_attached_to_top_level_config(_clear_image_env):
    # Use the default test=None branch — that auto-detects PYTEST_CURRENT_TEST
    # and reads TEST_-prefixed vars for the other required fields
    # (POSTGRES_*, HOST_NAME, APP_NAME, …). Our _clear_image_env fixture
    # removes both prefixed and unprefixed IMAGE_* vars, so we get defaults
    # for the image namespace.
    config = Config.from_env()
    assert isinstance(config.image, ImageConfig)
    assert config.image.max_upload_bytes == 5 * 1024 * 1024
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `mise run test -- tests/test_image_config.py -v`
Expected: collection error / ImportError — `ImageConfig` does not exist yet.

- [ ] **Step 3: Add `ImageConfig` class and wire it into `Config`**

In `src/babytroc/infrastructure/config.py`, add the new class above `class Config(NamedTuple):`:

```python
class ImageConfig(NamedTuple):
    max_upload_bytes: int
    max_pixels: int
    max_concurrent_processing_per_worker: int

    @classmethod
    def from_env(cls, *, test: bool | None = None) -> Self:
        env = EnvironmentVariablesReader(test=test)
        return cls(
            max_upload_bytes=int(
                env.get(
                    "IMAGE_MAX_UPLOAD_BYTES",
                    default=str(5 * 1024 * 1024),
                ),
            ),
            max_pixels=int(
                env.get(
                    "IMAGE_MAX_PIXELS",
                    default="16000000",
                ),
            ),
            max_concurrent_processing_per_worker=int(
                env.get(
                    "IMAGE_MAX_CONCURRENT_PROCESSING_PER_WORKER",
                    default="4",
                ),
            ),
        )
```

Add `image: ImageConfig` to the `Config` NamedTuple fields (place it next to `s3: S3Config`):

```python
class Config(NamedTuple):
    host_name: str
    app_name: str
    root_path: str
    test: bool
    delay: float
    database: DatabaseConfig
    pubsub: PubsubConfig
    email: EmailConfig
    s3: S3Config
    image: ImageConfig
    redis: RedisConfig
    auth: AuthConfig
    contact: ContactConfig
    cap: CapConfig
    signup: RateLimitConfig
    password_reset: RateLimitConfig
    item_create: RateLimitConfig
    image_upload: RateLimitConfig
```

Add `image: ImageConfig | None = None` to the `Config.from_env` signature (next to `s3`), default-construct it if `None`, and pass through:

```python
    @classmethod
    def from_env(  # noqa: C901
        cls,
        *,
        host_name: str | None = None,
        app_name: str | None = None,
        root_path: str | None = None,
        delay: float | None = None,
        database: DatabaseConfig | None = None,
        pubsub: PubsubConfig | None = None,
        email: EmailConfig | None = None,
        s3: S3Config | None = None,
        image: ImageConfig | None = None,
        redis: RedisConfig | None = None,
        auth: AuthConfig | None = None,
        contact: ContactConfig | None = None,
        cap: CapConfig | None = None,
        signup: RateLimitConfig | None = None,
        password_reset: RateLimitConfig | None = None,
        item_create: RateLimitConfig | None = None,
        image_upload: RateLimitConfig | None = None,
        test: bool | None = None,
    ) -> Self:
```

Just after the existing `if s3 is None: s3 = S3Config.from_env(test=test)` block, add:

```python
        if image is None:
            image = ImageConfig.from_env(test=test)
```

In the `return cls(...)` block, add `image=image,` (next to `s3=s3,`):

```python
        return cls(
            host_name=host_name,
            app_name=app_name,
            root_path=root_path,
            test=test,
            delay=delay,
            database=database,
            pubsub=pubsub,
            email=email,
            s3=s3,
            image=image,
            redis=redis,
            auth=auth,
            contact=contact,
            cap=cap,
            signup=signup,
            password_reset=password_reset,
            item_create=item_create,
            image_upload=image_upload,
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `mise run test -- tests/test_image_config.py -v`
Expected: 3 tests pass.

- [ ] **Step 5: Verify nothing else broke**

Run: `mise run lint && mise run test -- tests/test_config.py -v`
Expected: lint clean; `tests/test_config.py` still passes.

- [ ] **Step 6: Commit**

```bash
git add src/babytroc/infrastructure/config.py tests/test_image_config.py
git commit -m "add ImageConfig with upload-bytes, pixels, and per-worker concurrency limits"
```

---

### Task 2: Add the three new image error classes

**Files:**
- Create: `tests/test_image_errors.py`
- Modify: `src/babytroc/domains/image/errors.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_image_errors.py`:

```python
from http import HTTPStatus

from babytroc.domains.image.errors import (
    ImagePixelLimitError,
    ImageTooLargeError,
    InvalidImageError,
)


def test_image_too_large_error_uses_413():
    error = ImageTooLargeError(actual=2048, limit=1024)
    assert error.status_code == HTTPStatus.REQUEST_ENTITY_TOO_LARGE
    assert "2048" in error.message
    assert "1024" in error.message


def test_image_pixel_limit_error_uses_400():
    error = ImagePixelLimitError(max_pixels=16_000_000)
    assert error.status_code == HTTPStatus.BAD_REQUEST
    assert "16000000" in error.message


def test_invalid_image_error_uses_400():
    error = InvalidImageError()
    assert error.status_code == HTTPStatus.BAD_REQUEST
    assert error.message
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `mise run test -- tests/test_image_errors.py -v`
Expected: ImportError — these classes don't exist yet.

- [ ] **Step 3: Add the three classes**

Replace the contents of `src/babytroc/domains/image/errors.py` with:

```python
from collections.abc import Mapping
from http import HTTPStatus
from typing import Any

from babytroc.shared.errors import ApiError, BadRequestError, ConflictError, NotFoundError


class ItemImageError(ApiError):
    """Exception related to an item image."""


class ItemImageNotFoundError(ItemImageError, NotFoundError):
    """Exception raised when an item image is not found."""

    def __init__(self, key: Mapping[str, Any], **kwargs):
        super().__init__(
            datatype="image",
            key=key,
        )


class ItemImageNotOwnedError(ItemImageError, ConflictError):
    """Exception raised when an item image is used but not owned by user."""

    def __init__(self, image_name_user_id: tuple[str, int] | set[tuple[str, int]]):
        super().__init__(
            "The following image(s) are not owned by the user (image_name, user_id): "
            f"{image_name_user_id}"
        )


class ImageTooLargeError(ItemImageError):
    """Raised when an uploaded image exceeds the byte-size cap."""

    def __init__(self, actual: int, limit: int):
        super().__init__(
            f"Image too large: {actual} bytes (max {limit})",
            status_code=HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
        )


class ImagePixelLimitError(ItemImageError, BadRequestError):
    """Raised when an image's pixel count exceeds the decompression-bomb cap."""

    def __init__(self, max_pixels: int):
        super().__init__(f"Image exceeds max pixel count of {max_pixels}")


class InvalidImageError(ItemImageError, BadRequestError):
    """Raised when the uploaded bytes are not a recognisable image."""

    def __init__(self):
        super().__init__("Invalid or unreadable image file")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `mise run test -- tests/test_image_errors.py -v`
Expected: 3 tests pass.

- [ ] **Step 5: Verify nothing else broke**

Run: `mise run lint`
Expected: clean.

- [ ] **Step 6: Commit**

```bash
git add src/babytroc/domains/image/errors.py tests/test_image_errors.py
git commit -m "add ImageTooLargeError, ImagePixelLimitError, InvalidImageError"
```

---

### Task 3: Add `configure_pillow_pixel_limit` helper

**Files:**
- Modify: `src/babytroc/shared/image.py`
- Modify: `tests/test_image_variants.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_image_variants.py`:

```python
def test_configure_pillow_pixel_limit_sets_pil_global():
    from babytroc.shared.image import configure_pillow_pixel_limit

    original = PIL.Image.MAX_IMAGE_PIXELS
    try:
        configure_pillow_pixel_limit(12_345)
        assert PIL.Image.MAX_IMAGE_PIXELS == 12_345
    finally:
        PIL.Image.MAX_IMAGE_PIXELS = original
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `mise run test -- tests/test_image_variants.py::test_configure_pillow_pixel_limit_sets_pil_global -v`
Expected: ImportError or AttributeError — function not defined.

- [ ] **Step 3: Add the helper**

In `src/babytroc/shared/image.py`, after the existing imports, add:

```python
def configure_pillow_pixel_limit(max_pixels: int) -> None:
    """Set PIL's decompression-bomb cap (module-global PIL state)."""
    PIL.Image.MAX_IMAGE_PIXELS = max_pixels
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `mise run test -- tests/test_image_variants.py -v`
Expected: existing 4 tests still pass plus the new one — 5 passing.

- [ ] **Step 5: Commit**

```bash
git add src/babytroc/shared/image.py tests/test_image_variants.py
git commit -m "add configure_pillow_pixel_limit helper for decompression-bomb cap"
```

---

### Task 4: Add `infrastructure/image_processing.py` dependency module

**Files:**
- Create: `src/babytroc/infrastructure/image_processing.py`
- Create: `tests/test_image_processing_dep.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_image_processing_dep.py`:

```python
import asyncio

import pytest

from babytroc.infrastructure.image_processing import (
    get_image_processing_semaphore,
    init_image_processing_dependency,
)


def test_init_and_get_returns_same_semaphore():
    sem = asyncio.Semaphore(3)
    init_image_processing_dependency(sem)
    assert get_image_processing_semaphore() is sem


def test_init_overwrites_previous_semaphore():
    init_image_processing_dependency(asyncio.Semaphore(1))
    new_sem = asyncio.Semaphore(5)
    init_image_processing_dependency(new_sem)
    assert get_image_processing_semaphore() is new_sem


async def test_semaphore_is_usable_as_async_context_manager():
    init_image_processing_dependency(asyncio.Semaphore(2))
    sem = get_image_processing_semaphore()
    async with sem:
        assert sem._value == 1  # noqa: SLF001
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `mise run test -- tests/test_image_processing_dep.py -v`
Expected: ImportError — module does not exist.

- [ ] **Step 3: Create the module**

Create `src/babytroc/infrastructure/image_processing.py`:

```python
import asyncio

_image_processing_semaphore: asyncio.Semaphore


def init_image_processing_dependency(semaphore: asyncio.Semaphore) -> None:
    global _image_processing_semaphore  # noqa: PLW0603
    _image_processing_semaphore = semaphore


def get_image_processing_semaphore() -> asyncio.Semaphore:
    return _image_processing_semaphore
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `mise run test -- tests/test_image_processing_dep.py -v`
Expected: 3 tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/babytroc/infrastructure/image_processing.py tests/test_image_processing_dep.py
git commit -m "add image_processing infrastructure module with semaphore dependency"
```

---

### Task 5: Rewrite `upload_image` service

**Files:**
- Modify: `src/babytroc/domains/image/services/create.py`
- Create: `tests/image/test_upload_image_service.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/image/test_upload_image_service.py`:

```python
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
    """Return a minimal PNG header declaring `width`×`height`.

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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `mise run test -- tests/image/test_upload_image_service.py -v`
Expected: failures — the service still has the old signature (`fp: IO[bytes]`) and does not raise the new error types.

- [ ] **Step 3: Rewrite the service**

Replace the contents of `src/babytroc/domains/image/services/create.py` with:

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
        .values(
            {
                "name": name,
                "owner_id": owner_id,
            },
        )
        .returning(ItemImage)
    )

    try:
        res = await db.execute(stmt)
        item_image = res.unique().scalars().one()

    except IntegrityError as error:
        await get_user(
            db=db,
            user_id=owner_id,
        )
        raise error

    return ItemImageRead.model_validate(item_image)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `mise run test -- tests/image/test_upload_image_service.py -v`
Expected: 4 tests pass. (Decompression-bomb test relies on `configure_pillow_pixel_limit` being applied inside the test.)

- [ ] **Step 5: Run lint to catch import / type issues**

Run: `mise run lint`
Expected: clean. If mypy complains about call sites of `upload_image` (the router and seed), that's fine — Task 7 and Task 8 fix those. Note the failures for review but don't block here.

- [ ] **Step 6: Commit**

```bash
git add src/babytroc/domains/image/services/create.py tests/image/test_upload_image_service.py
git commit -m "rewrite upload_image service to accept bytes and offload PIL to thread"
```

---

### Task 6: Wire `create_app()` to configure PIL limit and init the semaphore

**Files:**
- Modify: `src/babytroc/app.py`

- [ ] **Step 1: Update imports**

In `src/babytroc/app.py`, replace the existing infrastructure imports block with:

```python
from .infrastructure.cache import init_cache_dependency
from .infrastructure.cache_client import RedisCache
from .infrastructure.config import Config
from .infrastructure.database import create_session_maker, init_db_session_dependency
from .infrastructure.email import init_email_dependency
from .infrastructure.image_processing import init_image_processing_dependency
from .infrastructure.pubsub import init_broadcast_dependency
from .infrastructure.redis import create_redis_client
```

Add an import for the new helper at the top of the file (next to `import babytroc.domains`):

```python
from babytroc.shared.image import configure_pillow_pixel_limit
```

- [ ] **Step 2: Configure PIL limit and init semaphore inside `create_app()`**

Inside `create_app()`, immediately after the existing `app.state.config = config` line, add:

```python
    # Image processing setup
    configure_pillow_pixel_limit(config.image.max_pixels)
    init_image_processing_dependency(
        asyncio.Semaphore(config.image.max_concurrent_processing_per_worker),
    )
```

(`asyncio` is already imported at the top of `app.py`.)

- [ ] **Step 3: Run the full test suite**

Run: `mise run test`
Expected: existing tests continue to pass (the router still uses the old signature, but only the image-upload tests touch it; those will fail in the next task and we'll fix them there). If you want to scope the run, target `mise run test -- tests/test_image_processing_dep.py tests/test_image_config.py tests/test_image_errors.py tests/image/test_upload_image_service.py -v` and check it's green.

Note: `tests/image/test_image_upload_rate_limit.py` may fail here because the router has not been updated yet to pass the semaphore — that is expected and will be fixed in Task 7.

- [ ] **Step 4: Commit**

```bash
git add src/babytroc/app.py
git commit -m "wire image processing setup into create_app (PIL limit + semaphore)"
```

---

### Task 7: Update the router

**Files:**
- Modify: `src/babytroc/routers/v1/images/create.py`
- Create: `tests/image/test_image_upload.py`

- [ ] **Step 1: Write the failing HTTP integration tests**

Create `tests/image/test_image_upload.py`:

```python
import io
import struct
import zlib
from http import HTTPStatus

import PIL.Image
import pytest
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `mise run test -- tests/image/test_image_upload.py -v`
Expected: failures — the router still passes `fp=file.file` to a service that no longer accepts that kwarg.

- [ ] **Step 3: Rewrite the router**

Replace the contents of `src/babytroc/routers/v1/images/create.py` with:

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

- [ ] **Step 4: Run tests to verify they pass**

Run: `mise run test -- tests/image/test_image_upload.py -v`
Expected: 4 tests pass.

- [ ] **Step 5: Re-run the rate-limit test that was failing before**

Run: `mise run test -- tests/image/test_image_upload_rate_limit.py -v`
Expected: passes (it only relies on the upload happy path, which is restored now).

- [ ] **Step 6: Run lint**

Run: `mise run lint`
Expected: clean.

- [ ] **Step 7: Commit**

```bash
git add src/babytroc/routers/v1/images/create.py tests/image/test_image_upload.py
git commit -m "enforce upload byte cap in image router and route through semaphore"
```

---

### Task 8: Update the seed script

**Files:**
- Modify: `src/babycli/seed/items.py`

- [ ] **Step 1: Update the wrapper to take bytes + semaphore**

In `src/babycli/seed/items.py`, replace the top-level `upload_image` wrapper (currently lines 49–65) with:

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

Add the `asyncio` import at the top of the file (sorted with the existing imports):

```python
import asyncio
import logging
```

- [ ] **Step 2: Build the semaphore once in `populate_items` and thread it through**

In `populate_items` (currently around line 119), add semaphore + PIL limit setup at the top of the function (right after `config = get_config()`):

```python
    configure_pillow_pixel_limit(config.image.max_pixels)
    semaphore = asyncio.Semaphore(
        config.image.max_concurrent_processing_per_worker,
    )
```

Add the import at the top of the file:

```python
from babytroc.shared.image import configure_pillow_pixel_limit
```

Update the `upload_image(...)` call inside the list comprehension to pass the new `semaphore`:

```python
        images[user.id] = [
            await upload_image(
                db=db,
                config=config,
                semaphore=semaphore,
                fp=fp,
                owner_id=user.id,
            )
            for fp in tqdm(images_fp)
        ]
```

- [ ] **Step 3: Run the seed-dependent tests**

Run: `mise run test -- tests/babycli/ -v`
Expected: passes. Also run `mise run lint` for unused-import/type checks.

- [ ] **Step 4: Commit**

```bash
git add src/babycli/seed/items.py
git commit -m "update seed upload_image to read bytes and pass per-worker semaphore"
```

---

### Task 9: Add concurrency and event-loop-responsiveness tests

**Files:**
- Create: `tests/image/test_image_upload_concurrency.py`

- [ ] **Step 1: Write the tests**

Create `tests/image/test_image_upload_concurrency.py`:

```python
import asyncio
import io
import threading
import time

import PIL.Image
import pytest
from httpx import AsyncClient

from babytroc.domains.image.services import create as create_service
from babytroc.infrastructure.image_processing import (
    get_image_processing_semaphore,
    init_image_processing_dependency,
)


SEMAPHORE_LIMIT = 2


def _png_bytes() -> bytes:
    img = PIL.Image.new("RGB", (400, 400), color="red")
    fp = io.BytesIO()
    img.save(fp, format="PNG")
    return fp.getvalue()


@pytest.fixture
def tight_semaphore():
    """Replace the global semaphore with a 2-slot one for the duration of the test."""
    original = get_image_processing_semaphore()
    init_image_processing_dependency(asyncio.Semaphore(SEMAPHORE_LIMIT))
    yield SEMAPHORE_LIMIT
    init_image_processing_dependency(original)


async def test_semaphore_bounds_concurrent_uploads(
    alice_client: AsyncClient,
    tight_semaphore: int,
    monkeypatch: pytest.MonkeyPatch,
):
    """N > limit parallel uploads must serialize down to <= limit in-flight."""

    in_flight = 0
    peak = 0
    lock = threading.Lock()
    original = create_service.image_utils.generate_webp_variants

    def slow_generate(fp):
        # Runs inside the asyncio.to_thread worker. Use threading.Lock to
        # protect the shared counters across worker threads.
        nonlocal in_flight, peak
        with lock:
            in_flight += 1
            peak = max(peak, in_flight)
        try:
            time.sleep(0.2)
            return original(fp)
        finally:
            with lock:
                in_flight -= 1

    monkeypatch.setattr(
        create_service.image_utils,
        "generate_webp_variants",
        slow_generate,
    )

    data = _png_bytes()

    async def one_upload():
        return await alice_client.post(
            "/api/v1/images",
            files={"file": ("x.png", io.BytesIO(data), "image/png")},
        )

    responses = await asyncio.gather(*(one_upload() for _ in range(6)))

    for r in responses:
        # Allow 429 in case rate limiting kicks in across test runs;
        # the bound assertion below is what matters.
        assert r.status_code in (201, 429), r.text
    assert peak <= tight_semaphore, (
        f"peak in-flight {peak} exceeded limit {tight_semaphore}"
    )


async def test_event_loop_remains_responsive_during_upload(
    alice_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """A lightweight GET must not be blocked by a concurrent slow upload."""

    original = create_service.image_utils.generate_webp_variants

    def slow_generate(fp):
        time.sleep(0.5)
        return original(fp)

    monkeypatch.setattr(
        create_service.image_utils,
        "generate_webp_variants",
        slow_generate,
    )

    data = _png_bytes()

    upload_task = asyncio.create_task(
        alice_client.post(
            "/api/v1/images",
            files={"file": ("x.png", io.BytesIO(data), "image/png")},
        ),
    )

    # Give the upload a moment to enter the to_thread call.
    await asyncio.sleep(0.05)

    t0 = time.monotonic()
    health = await alice_client.get("/api/v1/utils/regions")
    elapsed = time.monotonic() - t0

    assert health.status_code == 200
    assert elapsed < 0.2, (
        f"GET /api/v1/utils/regions took {elapsed:.3f}s while upload was in flight"
    )

    await upload_task
```

- [ ] **Step 2: Run the tests**

Run: `mise run test -- tests/image/test_image_upload_concurrency.py -v`
Expected: both tests pass. If `test_event_loop_remains_responsive_during_upload` fails with `elapsed >= 0.2s`, the `to_thread` offload is not actually being used — check Task 5 step 3 was applied. If `test_semaphore_bounds_concurrent_uploads` fails because too many requests are in-flight, the semaphore is not being acquired — check Task 7 step 3 wiring.

- [ ] **Step 3: Commit**

```bash
git add tests/image/test_image_upload_concurrency.py
git commit -m "add image upload concurrency cap and event-loop responsiveness tests"
```

---

### Task 10: Final validation

- [ ] **Step 1: Run full lint**

Run: `mise run lint`
Expected: clean.

- [ ] **Step 2: Run the full test suite**

Run: `mise run test`
Expected: all tests pass. If anything image-related still fails, look first at:
- `tests/image/test_image_upload_rate_limit.py` (PBM happy path)
- Anywhere else that uploads images during fixture seeding (chain seeds in `tests/fixtures/database/seeds/`)

- [ ] **Step 3: Verify the `# TODO limite upload size (middleware)` comment is gone**

Run: `grep -rn "limite upload size" src/`
Expected: no results.

- [ ] **Step 4: No-op commit only if cleanup needed**

If steps 1–3 surfaced anything you fixed, commit with a small message. Otherwise, this task ends without a new commit.

---

## Self-Review Notes (for the engineer)

- **Per-worker concurrency** — the semaphore is per uvicorn worker process. Real concurrent decode count is `WORKERS × max_concurrent_processing_per_worker`. The env var name reflects this; the spec covers the memory math.
- **Defense-in-depth byte cap** — both the router and the service check `len(data)` against `max_upload_bytes`. This is intentional, not a duplicate; the service guard protects internal callers (seed, future jobs) that bypass the router.
- **Decompression-bomb mechanism** — PIL's `MAX_IMAGE_PIXELS` is checked during `Image.open()` against the header-declared dimensions, so bombs are rejected without allocating the full decoded buffer. The helper `configure_pillow_pixel_limit` is called once at app startup (Task 6) and once at babycli seed startup (Task 8).
- **PIL exceptions caught**: `DecompressionBombError`, `UnidentifiedImageError`, `OSError`, `SyntaxError`. All other exceptions still bubble (intentional — those would be real bugs, not user-input issues).
- **Async semaphore lifetime** — `asyncio.Semaphore()` in Python 3.10+ does not bind to a loop at construction time, so creating it in the sync `create_app()` and in babycli setup is safe; it binds on first `.acquire()`.
