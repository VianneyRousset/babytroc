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


@pytest.mark.usefixtures("_clear_image_env")
def test_image_config_defaults():
    config = ImageConfig.from_env(test=False)
    assert config.max_upload_bytes == 5 * 1024 * 1024
    assert config.max_pixels == 16_000_000
    assert config.max_concurrent_processing_per_worker == 4


@pytest.mark.usefixtures("_clear_image_env")
def test_image_config_env_overrides(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("IMAGE_MAX_UPLOAD_BYTES", "10485760")
    monkeypatch.setenv("IMAGE_MAX_PIXELS", "8000000")
    monkeypatch.setenv("IMAGE_MAX_CONCURRENT_PROCESSING_PER_WORKER", "8")

    config = ImageConfig.from_env(test=False)

    assert config.max_upload_bytes == 10_485_760
    assert config.max_pixels == 8_000_000
    assert config.max_concurrent_processing_per_worker == 8


@pytest.mark.usefixtures("_clear_image_env")
def test_image_config_is_attached_to_top_level_config():
    # Use the default test=None branch — that auto-detects PYTEST_CURRENT_TEST
    # and reads TEST_-prefixed vars for the other required fields
    # (POSTGRES_*, HOST_NAME, APP_NAME, …). Our _clear_image_env fixture
    # removes both prefixed and unprefixed IMAGE_* vars, so we get defaults
    # for the image namespace.
    config = Config.from_env()
    assert isinstance(config.image, ImageConfig)
    assert config.image.max_upload_bytes == 5 * 1024 * 1024
