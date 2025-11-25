import uuid
from typing import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.wishlist_api.shared.errors import problem

MAX_REQUEST_SIZE = 2 * 1024 * 1024


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id

        try:
            response: Response = await call_next(request)
        except Exception:
            return problem(
                status=500,
                title="Internal Server Error",
                detail="An unexpected error occurred.",
                extras={"correlation_id": correlation_id},
            )

        response.headers["X-Correlation-ID"] = correlation_id

        return response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_REQUEST_SIZE:
            return problem(
                status=413,
                title="Payload Too Large",
                detail="Request body exceeds 2MB limit",
                type_="https://example.com/docs/errors/request-too-large",
            )
        return await call_next(request)
