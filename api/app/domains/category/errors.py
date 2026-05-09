from app.shared.errors import ApiError, NotFoundError


class CategoryError(ApiError):
    domain = "category"


class CategoryNotFoundError(CategoryError, NotFoundError):
    message = "Category not found."
