# S3 Image Storage Migration — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace imgpush with S3 (MinIO) + nginx for image storage; generate 3 webp variants on upload; clients build image URLs directly.

**Architecture:** API uploads processed webp images to S3 via aioboto3. Nginx reverse-proxies the bucket for public reads. The API no longer serves image bytes — the image read endpoint is removed and clients construct URLs from a base URL + image name + size suffix.

**Tech Stack:** aioboto3, Pillow (existing), FastAPI, SQLAlchemy async

---

### Task 1: Add aioboto3 dependency

**Files:**
- Modify: `pyproject.toml:5-25`

- [ ] **Step 1: Add aioboto3 to dependencies**

In `pyproject.toml`, add `"aioboto3>=13.0.0"` to the `dependencies` list (after `"aiohttp>=3.13.2"`). Also remove `"aiohttp>=3.13.2"` since it will no longer be needed (aioboto3 pulls in aiohttp transitively, but the codebase won't use aiohttp directly anymore).

Actually — keep `aiohttp` because `aiohttp-asgi-connector` still depends on it. Only add `aioboto3`:

```toml
dependencies = [
  "fastapi[standard]==0.*",
  "alembic>=1.15.2",
  "pillow>=11.2.1",
  "requests>=2.32.3",
  "pyjwt>=2.10.1",
  "uvicorn>=0.34.2",
  "websocket>=0.2.1",
  "broadcaster[redis] @ git+https://github.com/encode/broadcaster.git@6b3ea71d4f8fb038fa7d357a1fb3750d58ac614d",
  "redis[hiredis]>=5.0.0",
  "pydantic[email]",
  "fastapi-mail>=1.5.0",
  "bcrypt>=4.3.0",
  "posix-ipc>=1.3.2",
  "aiohttp>=3.13.2",
  "sqlalchemy>=2.0.38",
  "asyncpg-listen>=0.0.9",
  "asgi-lifespan==2.*",
  "aiohttp-asgi-connector>=1.1.0",
  "graphifyy>=0.4.1",
  "aioboto3>=13.0.0",
]
```

- [ ] **Step 2: Install**

Run: `uv sync`
Expected: installs aioboto3 + transitive deps (aiobotocore, botocore, etc.)

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "feat: add aioboto3 dependency for S3 image storage"
```

---

### Task 2: Replace ImgpushConfig with S3Config

**Files:**
- Modify: `app/config.py:118-129` (ImgpushConfig) and `app/config.py:178-246` (Config)

- [ ] **Step 1: Write the failing test**

Create `tests/test_s3_config.py`:

```python
import os

from app.config import S3Config


def test_s3_config_from_env(monkeypatch):
    monkeypatch.setenv("S3_ENDPOINT_URL", "http://minio:9000")
    monkeypatch.setenv("S3_ACCESS_KEY", "minioadmin")
    monkeypatch.setenv("S3_SECRET_KEY", "minioadmin")
    monkeypatch.setenv("S3_BUCKET", "babytroc-images")
    monkeypatch.setenv("S3_PUBLIC_URL", "https://images.babytroc.ch")

    config = S3Config.from_env()

    assert config.endpoint_url == "http://minio:9000"
    assert config.access_key == "minioadmin"
    assert config.secret_key == "minioadmin"
    assert config.bucket == "babytroc-images"
    assert config.public_url == "https://images.babytroc.ch"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_s3_config.py::test_s3_config_from_env -v`
Expected: FAIL with `ImportError: cannot import name 'S3Config'`

- [ ] **Step 3: Implement S3Config**

In `app/config.py`, replace the `ImgpushConfig` class (lines 118-128) with:

```python
class S3Config(NamedTuple):
    endpoint_url: str
    access_key: str
    secret_key: str
    bucket: str
    public_url: str

    @classmethod
    def from_env(
        cls,
        endpoint_url: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
        bucket: str | None = None,
        public_url: str | None = None,
    ) -> Self:
        if endpoint_url is None:
            endpoint_url = os.environ["S3_ENDPOINT_URL"]
        if access_key is None:
            access_key = os.environ["S3_ACCESS_KEY"]
        if secret_key is None:
            secret_key = os.environ["S3_SECRET_KEY"]
        if bucket is None:
            bucket = os.environ["S3_BUCKET"]
        if public_url is None:
            public_url = os.environ["S3_PUBLIC_URL"]

        return cls(
            endpoint_url=endpoint_url,
            access_key=access_key,
            secret_key=secret_key,
            bucket=bucket,
            public_url=public_url,
        )
```

In the `Config` class, replace `imgpush: ImgpushConfig` with `s3: S3Config`. Update `Config.from_env` — replace the `imgpush` parameter and builder:

```python
class Config(NamedTuple):
    host_name: str
    app_name: str
    test: bool
    delay: float
    database: DatabaseConfig
    pubsub: PubsubConfig
    email: EmailConfig
    s3: S3Config
    redis: RedisConfig
    auth: AuthConfig

    @classmethod
    def from_env(
        cls,
        *,
        host_name: str | None = None,
        app_name: str | None = None,
        test: bool | None = None,
        delay: float | None = None,
        database: DatabaseConfig | None = None,
        pubsub: PubsubConfig | None = None,
        email: EmailConfig | None = None,
        s3: S3Config | None = None,
        redis: RedisConfig | None = None,
        auth: AuthConfig | None = None,
    ) -> Self:
        # ... existing code for host_name through email ...

        if s3 is None:
            s3 = S3Config.from_env()

        # ... existing code for auth ...

        return cls(
            host_name=host_name,
            app_name=app_name,
            test=test,
            delay=delay,
            database=database,
            pubsub=pubsub,
            email=email,
            s3=s3,
            redis=redis,
            auth=auth,
        )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_s3_config.py::test_s3_config_from_env -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/config.py tests/test_s3_config.py
git commit -m "feat: replace ImgpushConfig with S3Config"
```

---

### Task 3: Create S3 client module

**Files:**
- Create: `app/clients/storage/__init__.py`
- Create: `app/clients/storage/s3.py`
- Test: `tests/test_s3_client.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_s3_client.py`:

```python
from io import BytesIO
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.clients.storage.s3 import delete_image_variants, upload_image_variants
from app.config import S3Config

TEST_S3_CONFIG = S3Config(
    endpoint_url="http://minio:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    bucket="test-bucket",
    public_url="https://images.example.com",
)


async def test_upload_image_variants():
    variants = {
        256: BytesIO(b"webp256"),
        512: BytesIO(b"webp512"),
        1024: BytesIO(b"webp1024"),
    }

    mock_s3_client = AsyncMock()

    with patch("app.clients.storage.s3._get_s3_client") as mock_get:
        mock_ctx = AsyncMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_s3_client)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)
        mock_get.return_value = mock_ctx

        await upload_image_variants(
            config=TEST_S3_CONFIG,
            name="abc123",
            variants=variants,
        )

    assert mock_s3_client.put_object.call_count == 3

    call_keys = {
        call.kwargs["Key"] for call in mock_s3_client.put_object.call_args_list
    }
    assert call_keys == {"abc123_256.webp", "abc123_512.webp", "abc123_1024.webp"}

    for call in mock_s3_client.put_object.call_args_list:
        assert call.kwargs["Bucket"] == "test-bucket"
        assert call.kwargs["ContentType"] == "image/webp"


async def test_delete_image_variants():
    mock_s3_client = AsyncMock()

    with patch("app.clients.storage.s3._get_s3_client") as mock_get:
        mock_ctx = AsyncMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_s3_client)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)
        mock_get.return_value = mock_ctx

        await delete_image_variants(
            config=TEST_S3_CONFIG,
            name="abc123",
        )

    assert mock_s3_client.delete_objects.call_count == 1
    call_kwargs = mock_s3_client.delete_objects.call_args.kwargs
    assert call_kwargs["Bucket"] == "test-bucket"
    keys = [obj["Key"] for obj in call_kwargs["Delete"]["Objects"]]
    assert set(keys) == {"abc123_256.webp", "abc123_512.webp", "abc123_1024.webp"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_s3_client.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'app.clients.storage'`

- [ ] **Step 3: Implement S3 client**

Create `app/clients/storage/__init__.py`:

```python
```

Create `app/clients/storage/s3.py`:

```python
import asyncio
from io import BytesIO

import aioboto3

from app.config import S3Config

IMAGE_SIZES = (256, 512, 1024)


def _get_s3_client(config: S3Config):
    session = aioboto3.Session()
    return session.client(
        "s3",
        endpoint_url=config.endpoint_url,
        aws_access_key_id=config.access_key,
        aws_secret_access_key=config.secret_key,
    )


def image_key(name: str, size: int) -> str:
    return f"{name}_{size}.webp"


async def upload_image_variants(
    config: S3Config,
    name: str,
    variants: dict[int, BytesIO],
) -> None:
    async with _get_s3_client(config) as client:
        await asyncio.gather(
            *(
                client.put_object(
                    Bucket=config.bucket,
                    Key=image_key(name, size),
                    Body=data.getvalue(),
                    ContentType="image/webp",
                )
                for size, data in variants.items()
            )
        )


async def delete_image_variants(
    config: S3Config,
    name: str,
) -> None:
    async with _get_s3_client(config) as client:
        await client.delete_objects(
            Bucket=config.bucket,
            Delete={
                "Objects": [
                    {"Key": image_key(name, size)} for size in IMAGE_SIZES
                ],
            },
        )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_s3_client.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/clients/storage/__init__.py app/clients/storage/s3.py tests/test_s3_client.py
git commit -m "feat: add S3 client for image upload and delete"
```

---

### Task 4: Update image utils — add webp variant generation

**Files:**
- Modify: `app/utils/image.py`
- Modify: `app/services/image/constants.py`
- Test: `tests/test_image_variants.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_image_variants.py`:

```python
from io import BytesIO

import PIL.Image

from app.utils.image import generate_webp_variants


def test_generate_webp_variants_produces_three_sizes():
    # Create a 2000x1000 test image
    img = PIL.Image.new("RGB", (2000, 1000), color="red")
    fp = BytesIO()
    img.save(fp, format="PNG")
    fp.seek(0)

    variants = generate_webp_variants(fp)

    assert set(variants.keys()) == {256, 512, 1024}

    for size, data in variants.items():
        result = PIL.Image.open(data)
        assert result.format == "WEBP"
        # Max dimension should equal the target size
        assert max(result.size) == size


def test_generate_webp_variants_small_image_not_upscaled():
    # Create a 100x50 test image — smaller than all targets
    img = PIL.Image.new("RGB", (100, 50), color="blue")
    fp = BytesIO()
    img.save(fp, format="PNG")
    fp.seek(0)

    variants = generate_webp_variants(fp)

    for _size, data in variants.items():
        result = PIL.Image.open(data)
        # Should not be upscaled — stays at 100x50
        assert result.size == (100, 50)


def test_generate_webp_variants_strips_exif():
    img = PIL.Image.new("RGB", (500, 500), color="green")
    exif = img.getexif()
    exif[0x0110] = "TestCamera"
    fp = BytesIO()
    img.save(fp, format="PNG", exif=exif.tobytes())
    fp.seek(0)

    variants = generate_webp_variants(fp)

    for _size, data in variants.items():
        result = PIL.Image.open(data)
        result_exif = result.getexif()
        assert 0x0110 not in result_exif


def test_generate_webp_variants_rejects_non_image():
    fp = BytesIO(b"not an image at all")

    try:
        generate_webp_variants(fp)
        assert False, "Should have raised"
    except Exception:
        pass
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_image_variants.py -v`
Expected: FAIL with `ImportError: cannot import name 'generate_webp_variants'`

- [ ] **Step 3: Implement generate_webp_variants**

Add to `app/utils/image.py`:

```python
def generate_webp_variants(
    fp: IO[bytes],
    sizes: tuple[int, ...] = (256, 512, 1024),
) -> dict[int, BytesIO]:
    """Load image, validate, process, and return webp variants for each size."""

    image = load_image(fp)

    # Validate — this will raise if the file is not a valid image.
    # We need to reload after verify() since it closes the image.
    image.verify()
    fp.seek(0)
    image = load_image(fp)

    image = apply_exif_orientation(image)
    image = clear_exif(image)

    variants: dict[int, BytesIO] = {}
    for size in sizes:
        resized = limit_image_size(image.copy(), size)
        buf = BytesIO()
        resized.save(buf, format="WEBP", quality=80)
        buf.seek(0)
        variants[size] = buf

    return variants
```

Update `app/services/image/constants.py`:

```python
MAX_DIMENSION = 1024
IMAGE_SIZES = (256, 512, 1024)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_image_variants.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/utils/image.py app/services/image/constants.py tests/test_image_variants.py
git commit -m "feat: add webp variant generation with security processing"
```

---

### Task 5: Rewrite image upload service to use S3

**Files:**
- Modify: `app/services/image/create.py`
- Modify: `app/services/image/__init__.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_image_upload_service.py`:

```python
from io import BytesIO
from unittest.mock import AsyncMock, patch

import PIL.Image
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.config import Config, S3Config
from app.schemas.image.read import ItemImageRead
from app.schemas.user.private import UserPrivateRead
from app.services.image.create import upload_image


async def test_upload_image_calls_s3_and_stores_in_db(
    app_config: Config,
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
):
    # Create a valid test image
    img = PIL.Image.new("RGB", (500, 500), color="red")
    fp = BytesIO()
    img.save(fp, format="PNG")
    fp.seek(0)

    with patch("app.services.image.create.s3.upload_image_variants") as mock_upload:
        mock_upload.return_value = None

        async with database_sessionmaker.begin() as session:
            result = await upload_image(
                config=app_config,
                db=session,
                fp=fp,
                owner_id=alice.id,
            )

        assert isinstance(result, ItemImageRead)
        assert result.owner_id == alice.id
        assert result.name  # UUID string, not empty

        # S3 upload was called with the correct name and 3 variants
        mock_upload.assert_called_once()
        call_kwargs = mock_upload.call_args.kwargs
        assert call_kwargs["config"] == app_config.s3
        assert call_kwargs["name"] == result.name
        assert set(call_kwargs["variants"].keys()) == {256, 512, 1024}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_image_upload_service.py -v`
Expected: FAIL — `upload_image` still imports imgpush

- [ ] **Step 3: Rewrite upload_image service**

Replace `app/services/image/create.py`:

```python
import uuid
from typing import IO

from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app import utils
from app.clients.storage import s3
from app.config import Config
from app.models.item.image import ItemImage
from app.schemas.image.read import ItemImageRead
from app.services.user.read import get_user


async def upload_image(
    config: Config,
    db: AsyncSession,
    *,
    owner_id: int,
    fp: IO[bytes],
) -> ItemImageRead:
    """Upload a new item image. Generates 3 webp variants and stores in S3."""

    # Process image and generate webp variants
    variants = utils.image.generate_webp_variants(fp)

    # Generate a unique name
    name = uuid.uuid4().hex

    # Upload all variants to S3
    await s3.upload_image_variants(
        config=config.s3,
        name=name,
        variants=variants,
    )

    # Create item image record in database
    stmt = (
        insert(ItemImage)
        .values(
            {
                "name": name,
                "owner_id": owner_id,
            }
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

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_image_upload_service.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/services/image/create.py
git commit -m "feat: rewrite image upload service to use S3 with webp variants"
```

---

### Task 6: Remove image read proxy and imgpush client

**Files:**
- Modify: `app/services/image/read.py` — remove `get_image_data`
- Modify: `app/services/image/__init__.py` — remove `get_image_data` export
- Modify: `app/routers/v1/images/read.py` — remove the proxy endpoint
- Modify: `app/routers/v1/images/__init__.py` — remove read import
- Delete: `app/clients/networking/imgpush/` — entire directory
- Delete: `app/schemas/networking/imgpush.py`
- Modify: `app/clients/networking/__init__.py` — remove imgpush import

- [ ] **Step 1: Remove get_image_data from service**

In `app/services/image/read.py`, remove the `get_image_data` function (lines 17-32) and remove the `from app.clients.networking import imgpush` import and `from app.config import Config` import.

The file should now contain only `get_many_images` and `check_image_owners`:

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.errors.image import ItemImageNotFoundError, ItemImageNotOwnedError
from app.models.item.image import ItemImage
from app.schemas.base import Base as SchemaBase
from app.schemas.image.read import ItemImageRead


class CheckImageOwner(SchemaBase):
    image_name: str
    owner_id: int


async def get_many_images(
    db: AsyncSession,
    image_names: set[str],
) -> list[ItemImageRead]:
    """Get all item images with the given image names.

    Raises ItemImageNotFoundError if not all images exist.
    """

    stmt = select(ItemImage).where(ItemImage.name.in_(image_names))

    images = (await db.execute(stmt)).unique().scalars().all()

    if len(images) != len(image_names):
        if missing_image_names := image_names - {img.name for img in images}:
            raise ItemImageNotFoundError({"image_names": missing_image_names})

        msg = (
            "The number of images read does not match the number of image names. "
            "Unexpected reason"
        )
        raise RuntimeError(msg)

    return [ItemImageRead.model_validate(img) for img in images]


async def check_image_owners(
    db: AsyncSession,
    image_owners: list[CheckImageOwner],
) -> None:
    """Raises ItemImageNotOwnedError if any of the given images is not owner by user.

    Also raises ItemImageNotFoundError if not all images exist.
    """

    images = await get_many_images(
        db=db,
        image_names={a.image_name for a in image_owners},
    )

    if missing_image_owners := (
        {(a.image_name, a.owner_id) for a in image_owners}
        - {(img.name, img.owner_id) for img in images}
    ):
        raise ItemImageNotOwnedError(missing_image_owners)
```

- [ ] **Step 2: Update services/image/__init__.py**

```python
from .create import upload_image

__all__ = [
    "upload_image",
]
```

- [ ] **Step 3: Remove the image read router endpoint**

Replace `app/routers/v1/images/read.py` — delete the entire file content and leave it empty, OR remove the file entirely. Since the router module's `__init__.py` imports `read`, the simplest fix is to keep the file but remove the endpoint:

```python
from .router import router  # noqa: F401
```

Update `app/routers/v1/images/__init__.py`:

```python
from . import create, read
from .router import router

__all__ = [
    "create",
    "read",
    "router",
]
```

(This can stay as-is since the read module still exists, just with no endpoints.)

- [ ] **Step 4: Delete imgpush client**

Delete the entire `app/clients/networking/imgpush/` directory:
- `app/clients/networking/imgpush/__init__.py`
- `app/clients/networking/imgpush/create.py`
- `app/clients/networking/imgpush/read.py`
- `app/clients/networking/imgpush/constants.py`

Delete `app/schemas/networking/imgpush.py`.

Update `app/clients/networking/__init__.py`:

```python
```

(Empty file — no more imgpush import.)

- [ ] **Step 5: Also delete the image query schema**

Delete `app/schemas/image/query.py` since it was only used by the removed read endpoint. (The `ItemImageQuery` with `size` param is no longer needed — clients pick 256/512/1024 themselves.)

- [ ] **Step 6: Verify lint passes**

Run: `mise run lint:ruff`
Expected: PASS (no references to deleted modules)

- [ ] **Step 7: Commit**

```bash
git rm app/clients/networking/imgpush/__init__.py app/clients/networking/imgpush/create.py app/clients/networking/imgpush/read.py app/clients/networking/imgpush/constants.py app/schemas/networking/imgpush.py app/schemas/image/query.py
git add app/services/image/read.py app/services/image/__init__.py app/routers/v1/images/read.py app/clients/networking/__init__.py
git commit -m "feat: remove imgpush client and image proxy endpoint"
```

---

### Task 7: Update test fixtures for S3

**Files:**
- Modify: `tests/fixtures/app.py` — add S3Config to test config
- Modify: `tests/fixtures/items.py` — image fixtures now go through S3 (mocked)
- Modify: `tests/item/test_item_images.py` — update test for removed read endpoint

- [ ] **Step 1: Update test app_config fixture**

In `tests/fixtures/app.py`, add `S3Config` import and pass it to `Config.from_env`:

```python
from collections.abc import AsyncGenerator

import pytest
import sqlalchemy
from asgi_lifespan import LifespanManager
from fastapi import FastAPI

from app.app import create_app
from app.config import Config, DatabaseConfig, PubsubConfig, RedisConfig, S3Config


@pytest.fixture(scope="class")
async def app_config(
    database: sqlalchemy.URL,
) -> Config:
    """App config."""

    redis_config = RedisConfig.from_env(db=3)

    return Config.from_env(
        database=DatabaseConfig.from_env(
            url=database,
        ),
        pubsub=PubsubConfig(url=redis_config.url),
        redis=redis_config,
        s3=S3Config(
            endpoint_url="http://localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            bucket="test-bucket",
            public_url="http://localhost:9000/test-bucket",
        ),
    )


@pytest.fixture(scope="class")
async def app(
    app_config: Config,
    database: sqlalchemy.URL,
) -> AsyncGenerator[FastAPI]:
    prefix = f"{database.database}:" if database.database else ""
    app = create_app(app_config, pubsub_channel_prefix=prefix)
    async with LifespanManager(app):
        yield app


@pytest.fixture(autouse=True, scope="class")
async def flush_redis_cache(app: FastAPI):
    """Flush Redis test DB before each test class."""
    await app.state.redis.flushdb()
    yield
    await app.state.redis.flushdb()
```

- [ ] **Step 2: Mock S3 in image upload fixtures**

The image upload fixtures in `tests/fixtures/items.py` call `services.image.upload_image` which now calls S3. We need to mock the S3 upload call so tests don't need a real MinIO instance.

Add a session-scoped autouse fixture in `tests/conftest.py` (or a new `tests/fixtures/s3.py` added to `pytest_plugins`):

Create `tests/fixtures/s3.py`:

```python
from unittest.mock import AsyncMock, patch

import pytest


@pytest.fixture(autouse=True, scope="session")
def mock_s3_uploads():
    """Mock S3 uploads globally for all tests."""
    with patch(
        "app.clients.storage.s3.upload_image_variants",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = None
        yield mock
```

Register in `tests/conftest.py` by adding `"tests.fixtures.s3"` to `pytest_plugins`.

- [ ] **Step 3: Update test_item_images.py**

The `test_created_image_can_be_read` test currently uploads then reads via `GET /api/v1/images/{name}`. The read endpoint is removed. Replace it with a test that just verifies upload succeeds and returns the expected shape:

```python
import pytest
from httpx import AsyncClient

from app.schemas.item.read import ItemRead
from tests.fixtures.items import ItemData


@pytest.mark.usefixtures("items")
class TestItemImages:
    """Test item images."""

    async def test_upload_image_returns_name(
        self,
        alice_client: AsyncClient,
        alice_items_image_data: bytes,
    ):
        """Upload image and verify response contains a name."""

        resp = await alice_client.post(
            "/api/v1/images",
            files={"file": alice_items_image_data},
        )
        resp.raise_for_status()
        data = resp.json()
        assert "name" in data
        assert len(data["name"]) == 32  # uuid hex

    async def test_item_images_order(
        self,
        alice_client: AsyncClient,
        alice_items_image_data: bytes,
        alice_new_item_data: ItemData,
    ):
        """Check that item images order respects the created/updated one."""

        # upload 5 images
        names: list[str] = [
            await self.upload_image(alice_client, alice_items_image_data)
            for _ in range(5)
        ]

        shuffled_names = [names[i] for i in [3, 4, 1, 0, 2]]

        # create item with custom order (different than upload order)
        resp = await alice_client.post(
            "/api/v1/me/items",
            json={
                **alice_new_item_data,
                "images": shuffled_names,
            },
        )
        resp.raise_for_status()
        item = resp.json()
        item_id = item["id"]

        # get item by id from global list
        resp = await alice_client.get(f"/api/v1/items/{item_id}")
        resp.raise_for_status()
        item = ItemRead.model_validate(resp.json())

        # check the order of the images is preserved
        assert item.image_names == shuffled_names

    @staticmethod
    async def upload_image(client: AsyncClient, img: bytes) -> str:
        resp = await client.post(
            "/api/v1/images",
            files={"file": img},
        )
        resp.raise_for_status()
        return resp.json()["name"]
```

- [ ] **Step 4: Run the full test suite**

Run: `mise run test`
Expected: PASS — all tests pass with S3 mocked globally

- [ ] **Step 5: Commit**

```bash
git add tests/fixtures/app.py tests/fixtures/s3.py tests/fixtures/items.py tests/item/test_item_images.py tests/conftest.py
git commit -m "test: update fixtures and tests for S3 migration"
```

---

### Task 8: Update CLAUDE.md and clean up

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Update env var docs in CLAUDE.md**

In the `### Environment` section, replace the `IMGPUSH_{HOST,PORT}` references with:

`S3_{ENDPOINT_URL,ACCESS_KEY,SECRET_KEY,BUCKET,PUBLIC_URL}` (MinIO S3 storage).

Remove any mention of imgpush from the project description at the top too — change "Image storage delegated to an `imgpush` service" to "Image storage via S3 (MinIO) with nginx reverse proxy for serving."

- [ ] **Step 2: Verify lint and tests pass**

Run: `mise run lint && mise run test`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md for S3 migration"
```

---

### Task 9: Final verification

- [ ] **Step 1: Run full lint**

Run: `mise run lint`
Expected: PASS — no ruff errors, no mypy errors referencing imgpush

- [ ] **Step 2: Run full test suite**

Run: `mise run test`
Expected: All tests PASS

- [ ] **Step 3: Verify no dangling imgpush references**

Run: `grep -r "imgpush" app/ tests/ --include="*.py"`
Expected: No results (only possibly in `__pycache__` which is fine)

- [ ] **Step 4: Verify no dangling imgpush schema references**

Run: `grep -r "ImgpushConfig\|imgpush" app/ --include="*.py"`
Expected: No results
