# Compatibility shim — real module has moved to app.infrastructure.storage
from app.infrastructure.storage import *  # noqa: F401,F403
from app.infrastructure.storage import (
    IMAGE_SIZES,
    delete_image_variants,
    image_key,
    upload_image_variants,
)
