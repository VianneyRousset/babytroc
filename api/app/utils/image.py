from enum import Enum
from io import BytesIO, IOBase

from PIL import Image


def load_image(fp: IOBase) -> Image:
    return Image.open(fp)


def serialize_image(image: Image, format="jpeg") -> IOBase:
    fp = BytesIO()
    image.save(fp, format=format)
    return fp


def limit_image_size(
    image: Image,
    max_dim: int,
) -> Image:
    aspect_ratio = image.width / image.height

    # image already small enough
    if image.width <= max_dim and image.height <= max_dim:
        return image

    if image.width > image.height:
        w = max_dim
        h = int(round(w / aspect_ratio))
    else:
        h = max_dim
        w = int(round(h * aspect_ratio))

    return image.resize(
        size=[w, h],
        resample=Image.Resampling.BILINEAR,
        reducing_gap=4.0,
    )


EXIF_ORIENTATION_TAG = 0x0112


class ExifOrientation(Enum):
    horizontal = 1
    mirror_horizontal = 2
    rotate_180 = 3
    mirror_vertical = 4
    mirror_horizontal_and_rotate_270_cw = 5
    rotate_90_cw = 6
    mirror_horizontal_and_rotate_90_cw = 7
    rotate_270_cw = 8


def get_exif_orientation(image: Image) -> ExifOrientation | None:
    exif = image.getexif()

    if not exif or EXIF_ORIENTATION_TAG not in exif:
        return None

    try:
        return ExifOrientation(exif[EXIF_ORIENTATION_TAG])

    except ValueError:
        return None


def apply_exif_orientation(image: Image) -> Image:
    orientation = get_exif_orientation(image)

    if orientation is None:
        return image

    match orientation:
        case ExifOrientation.horizontal:
            return image
        case ExifOrientation.mirror_horizontal:
            return image.transpose(Image.Transpose.MIRROR_HORIZONTAL)
        case ExifOrientation.rotate_180:
            return image.transpose(Image.Transpose.ROTATE_180)
        case ExifOrientation.mirror_vertical:
            return image.transpose(Image.Transpose.MIRROR_VERTICAL)
        case ExifOrientation.mirror_horizontal_and_rotate_270_cw:
            return image.transpose(Image.Transpose.TRANSPOSE)
        case ExifOrientation.rotate_90_cw:
            return image.transpose(Image.Transpose.ROTATE_270)
        case ExifOrientation.mirror_horizontal_and_rotate_90_cw:
            return image.transpose(Image.Transpose.TRANSVERSE)
        case ExifOrientation.rotate_270_cw:
            return image.transpose(Image.Transpose.ROTATE_90)


def clear_exif(image: Image) -> Image:
    exif = image.getexif()

    for k in set(exif.keys()):
        del exif[k]

    return image
