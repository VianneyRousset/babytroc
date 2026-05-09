from io import BytesIO
from unittest.mock import AsyncMock, patch

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
        128: BytesIO(b"webp128"),
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

    assert mock_s3_client.put_object.call_count == 4

    call_keys = {
        call.kwargs["Key"] for call in mock_s3_client.put_object.call_args_list
    }
    assert call_keys == {
        "abc123_128.webp",
        "abc123_256.webp",
        "abc123_512.webp",
        "abc123_1024.webp",
    }

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
    assert set(keys) == {
        "abc123_128.webp",
        "abc123_256.webp",
        "abc123_512.webp",
        "abc123_1024.webp",
    }
