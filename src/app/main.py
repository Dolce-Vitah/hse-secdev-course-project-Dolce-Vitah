from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.adapters.database import init_db
from src.app.api import auth, wishes
from src.shared.errors import AppError, InternalServerError, ValidationError

app = FastAPI(title="Wishlist API")

app.include_router(auth.router, prefix="/api/v1")
app.include_router(wishes.router, prefix="/api/v1")


@app.on_event("startup")
def on_startup():
    init_db()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    details = {"errors": exc.errors()}
    error = ValidationError(message="Invalid request data", details=details)
    return JSONResponse(
        status_code=error.status_code,
        content={
            "code": error.code,
            "message": error.message,
            "details": error.details,
        },
    )


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "message": exc.message, "details": exc.details},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    error = InternalServerError()
    return JSONResponse(
        status_code=error.status_code,
        content={"code": error.code, "message": error.message, "details": {}},
    )
