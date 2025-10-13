from fastapi import HTTPException, status


class AppError(HTTPException):
    def __init__(
        self, code: str, message: str, http_status: int, details: dict | None = None
    ):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(
            status_code=http_status,
            detail={"code": code, "message": message, "details": self.details},
        )


class ValidationError(AppError):
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(
            "VALIDATION_ERROR", message, status.HTTP_400_BAD_REQUEST, details
        )


class AuthenticationError(AppError):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__("UNAUTHORIZED", message, status.HTTP_401_UNAUTHORIZED)


class AuthorizationError(AppError):
    def __init__(self, message: str = "You are not allowed to perform this action"):
        super().__init__("FORBIDDEN", message, status.HTTP_403_FORBIDDEN)


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__("NOT_FOUND", message, status.HTTP_404_NOT_FOUND)


class UserAlreadyExistsError(AppError):
    def __init__(self, message: str = "User with this username already exists"):
        super().__init__("USER_ALREADY_EXISTS", message, status.HTTP_400_BAD_REQUEST)


class InternalServerError(AppError):
    def __init__(self, message: str = "Internal server error"):
        super().__init__(
            "INTERNAL_ERROR", message, status.HTTP_500_INTERNAL_SERVER_ERROR
        )
