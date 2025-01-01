from io import IOBase

from app.clients.networking import imgpush


def get_image_data(
    image_name: str,
) -> IOBase:
    """Get item by name."""

    # get item from databse
    fp = imgpush.get_image(image_name)

    return fp
