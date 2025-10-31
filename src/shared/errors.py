from typing import Any, Dict
from uuid import uuid4

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse


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


def problem(
    status: int,
    title: str,
    detail: str,
    type_: str = "about:blank",
    request: Request | None = None,
    extras: Dict[str, Any] | None = None,
) -> JSONResponse:
    if isinstance(detail, Exception):
        detail = str(detail)

    cid = (
        getattr(request.state, "correlation_id", str(uuid4()))
        if request
        else str(uuid4())
    )

    payload = {
        "type": type_,
        "title": title,
        "status": status,
        "detail": detail,
        "correlation_id": cid,
    }

    if extras:
        safe_extras = {k: str(v) for k, v in extras.items()}
        payload.update(safe_extras)

    response = JSONResponse(
        content=payload,
        status_code=status,
        media_type="application/problem+json",
    )

    response.headers["X-Correlation-ID"] = cid

    return response
