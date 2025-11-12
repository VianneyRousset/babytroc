from app.clients.networking import imgpush
from app.config import Config


def get_image_data(
    config: Config,
    image_name: str,
    *,
    size: int | None = None,
) -> bytes:
    """Get item by name."""

    # get item from databse
    image = imgpush.get_image(
        config=config,
        name=image_name,
        size=size,
    )

    return image
