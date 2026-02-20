class AppError(Exception):
    """Base application exception with explicit error codes."""

    def __init__(self, message: str, *, code: str = "app_error", status_code: int = 500) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class ResourceNotFoundError(AppError):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message=message, code="resource_not_found", status_code=404)
