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
    assert "invalid" in error.message.lower()
