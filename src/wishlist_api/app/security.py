import os
from datetime import datetime, timedelta

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session

from src.wishlist_api.adapters.database import get_session
from src.wishlist_api.domain.models import User
from src.wishlist_api.shared.errors import AuthenticationError, NotFoundError

from .utils.token_utils import is_token_revoked, revoke_token

USE_ENV_SECRETS = os.getenv("USE_ENV_SECRETS", "true").lower() == "true"
if not USE_ENV_SECRETS:
    raise RuntimeError(
        "Environment-based secrets " "are required (USE_ENV_SECRETS=true)"
    )

ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
JWT_ROTATE_KEY = os.getenv("JWT_ROTATE_KEY", "false").lower() == "true"

JWT_SECRET_CURRENT = os.getenv("JWT_SECRET_CURRENT", "wishlist-current")
JWT_SECRET_PREVIOUS = os.getenv("JWT_SECRET_PREVIOUS", "wishlist-previous")

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__memory_cost=65536,
    argon2__time_cost=3,
    argon2__parallelism=2,
)
bearer_scheme = HTTPBearer()


def get_password_hash(password: str) -> str:
    return str(pwd_context.hash(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bool(pwd_context.verify(plain_password, hashed_password))


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, JWT_SECRET_CURRENT, algorithm=ALGORITHM)
    return str(token)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),  # noqa: B008
    session: Session = Depends(get_session),  # noqa: B008
) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET_CURRENT, algorithms=[ALGORITHM])
    except JWTError:
        if JWT_ROTATE_KEY:
            try:
                payload = jwt.decode(token, JWT_SECRET_PREVIOUS, algorithms=[ALGORITHM])
            except JWTError:
                raise AuthenticationError("Invalid or malformed token")
        else:
            raise AuthenticationError("Invalid or malformed token")

    user_id: str = payload.get("sub")
    if user_id is None:
        raise AuthenticationError("Invalid token: no subject field")

    if is_token_revoked(session, token):
        raise AuthenticationError("Token has been revoked")

    user = session.get(User, int(user_id))
    if not user:
        raise NotFoundError("User not found")

    return user


def logout_user(token: str, session: Session) -> None:
    try:
        payload = jwt.decode(token, JWT_SECRET_CURRENT, algorithms=[ALGORITHM])
        exp = datetime.utcfromtimestamp(
            payload.get("exp", datetime.utcnow().timestamp())
        )
        revoke_token(session, token, exp)
    except JWTError:
        pass
