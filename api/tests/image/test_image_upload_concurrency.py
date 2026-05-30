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
