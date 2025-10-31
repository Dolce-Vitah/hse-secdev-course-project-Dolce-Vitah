from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError

from src.adapters.database import init_db
from src.app.api import auth, wishes
from src.app.middleware import CorrelationIdMiddleware, RequestSizeLimitMiddleware
from src.shared.errors import AppError, problem

app = FastAPI(title="Wishlist API")

app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(RequestSizeLimitMiddleware)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(wishes.router, prefix="/api/v1")


@app.on_event("startup")
def on_startup():
    init_db()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return problem(
        status=400,
        title="Validation Error",
        detail="Invalid request data",
        request=request,
        extras={"errors": exc.errors()},
    )


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return problem(
        status=exc.status_code,
        title=exc.code,
        detail=exc.message,
        request=request,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return problem(
        status=500,
        title="Internal Server Error",
        detail="An unexpected error occurred.",
        request=request,
    )
