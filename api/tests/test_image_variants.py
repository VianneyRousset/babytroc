from io import BytesIO

import PIL.Image
import pytest

from babytroc.shared.image import generate_webp_variants


def test_generate_webp_variants_produces_three_sizes():
    # Create a 2000x1000 test image
    img = PIL.Image.new("RGB", (2000, 1000), color="red")
    fp = BytesIO()
    img.save(fp, format="PNG")
    fp.seek(0)

    variants = generate_webp_variants(fp)

    assert set(variants.keys()) == {128, 256, 512, 1024}

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

    with pytest.raises(PIL.Image.UnidentifiedImageError):
        generate_webp_variants(fp)


def test_configure_pillow_pixel_limit_sets_pil_global():
    from babytroc.shared.image import configure_pillow_pixel_limit

    original = PIL.Image.MAX_IMAGE_PIXELS
    try:
        configure_pillow_pixel_limit(12_345)
        assert PIL.Image.MAX_IMAGE_PIXELS == 12_345
    finally:
        PIL.Image.MAX_IMAGE_PIXELS = original
