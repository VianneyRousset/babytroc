from io import IOBase

from app.clients.networking import imgpush
from app.config import Config


def get_image_data(
    config: Config,
    image_name: str,
) -> IOBase:
    """Get item by name."""

    # get item from databse
    fp = imgpush.get_image(config, image_name)

    return fp
