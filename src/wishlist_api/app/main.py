from typing import Dict

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.wishlist_api.adapters.database import init_db
from src.wishlist_api.app.api import auth, wishes
from src.wishlist_api.app.middleware import (
    CorrelationIdMiddleware,
    RequestSizeLimitMiddleware,
)
from src.wishlist_api.shared.errors import AppError, problem

app = FastAPI(title="Wishlist API")

app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(RequestSizeLimitMiddleware)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(wishes.router, prefix="/api/v1")


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return problem(
        status=422,
        title="Unprocessable Entity",
        detail="The request body is invalid.",
        request=request,
        extras={"errors": exc.errors()},
    )


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return problem(
        status=exc.status_code,
        title=exc.code,
        detail=exc.message,
        request=request,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return problem(
        status=500,
        title="Internal Server Error",
        detail="An unexpected error occurred.",
        request=request,
    )
