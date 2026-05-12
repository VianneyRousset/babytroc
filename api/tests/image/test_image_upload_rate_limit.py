import io
from typing import Any, Callable

from httpx import AsyncClient

from babytroc.routers.v1.images.create import rate_limit_image_upload


async def test_rate_limit_returns_429_after_limit(
    alice_client: AsyncClient,
    tight_rate_limit_factory: Callable[..., Any],
):
    tight_rate_limit_factory(
        dep=rate_limit_image_upload,
        key_prefix="image-upload-test",
        anon_limit=2, auth_limit=2, window_seconds=60,
    )

    # Minimal 1x1 PBM image (same format as alice_items_image_data fixture)
    pbm = "\n".join(["P1", "3 3", "101", "101", "010"]).encode()

    for _ in range(2):
        r = await alice_client.post(
            "/api/v1/images",
            files={"file": ("x.pbm", io.BytesIO(pbm), "image/x-portable-bitmap")},
        )
        assert r.status_code in (200, 201), r.text

    r3 = await alice_client.post(
        "/api/v1/images",
        files={"file": ("x.pbm", io.BytesIO(pbm), "image/x-portable-bitmap")},
    )
    assert r3.status_code == 429
