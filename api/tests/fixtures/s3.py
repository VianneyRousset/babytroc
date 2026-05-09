from unittest.mock import AsyncMock, patch

import pytest


@pytest.fixture(autouse=True, scope="session")
def mock_s3_uploads():
    """Mock S3 uploads globally for all tests."""
    with patch(
        "babytroc.infrastructure.storage.upload_image_variants",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = None
        yield mock
