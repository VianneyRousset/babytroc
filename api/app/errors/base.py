# Compatibility shim — canonical location: app.shared.errors
from app.shared.errors import ApiError, BadRequestError, ConflictError, NotFoundError

__all__ = ["ApiError", "BadRequestError", "ConflictError", "NotFoundError"]
