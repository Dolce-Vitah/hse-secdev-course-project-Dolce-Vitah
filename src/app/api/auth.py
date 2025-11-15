import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import DefaultDict, List

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlmodel import Session, select

from src.adapters.database import get_session
from src.app.security import (
    bearer_scheme,
    create_access_token,
    get_current_user,
    get_password_hash,
    logout_user,
    verify_password,
)
from src.domain.models import User, UserRole
from src.domain.schemas import Token, UserCreate
from src.shared.errors import (
    AuthenticationError,
    AuthorizationError,
    InternalServerError,
    NotFoundError,
    UserAlreadyExistsError,
)

router = APIRouter(prefix="/auth", tags=["auth"])

logger = logging.getLogger("audit")
logger.setLevel(logging.INFO)

FAILED_LOGINS: DefaultDict[str, List[datetime]] = defaultdict(list)
MAX_FAILED = 5
BLOCK_MINUTES = 15


def check_rate_limit(ip: str) -> None:
    now = datetime.utcnow()
    FAILED_LOGINS[ip] = [
        t for t in FAILED_LOGINS[ip] if now - t < timedelta(minutes=BLOCK_MINUTES)
    ]
    if len(FAILED_LOGINS[ip]) >= MAX_FAILED:
        raise AuthorizationError("Too many login attempts, try later")


def record_failed_attempt(ip: str) -> None:
    FAILED_LOGINS[ip].append(datetime.utcnow())


@router.post("/register", response_model=Token)
def register(
    user_in: UserCreate, session: Session = Depends(get_session)  # noqa B008
) -> Token:
    existing = session.exec(
        select(User).where(User.username == user_in.username)
    ).first()
    if existing:
        raise UserAlreadyExistsError()

    try:
        user = User(
            username=user_in.username,
            password_hash=get_password_hash(user_in.password),
            role=UserRole.user,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
    except Exception:
        raise InternalServerError()

    access_token = create_access_token(
        {"sub": str(user.id), "role": user.role.value},
        expires_delta=timedelta(minutes=15),  # TTL ≤ 15 минут
    )

    logger.info(f"User {user.id} registered")
    return Token(access_token=access_token, token_type="bearer")


@router.post("/login", response_model=Token)
def login(
    user_in: UserCreate,
    session: Session = Depends(get_session),  # noqa: B008
    ip: str | None = None,
) -> Token:
    if ip is None:
        ip = "127.0.0.1"
    check_rate_limit(ip)

    user = session.exec(select(User).where(User.username == user_in.username)).first()
    if not user or not verify_password(user_in.password, user.password_hash):
        record_failed_attempt(ip)
        raise AuthenticationError("Invalid credentials")

    access_token = create_access_token(
        {"sub": str(user.id), "role": user.role.value},
        expires_delta=timedelta(minutes=15),
    )

    logger.info(f"User {user.id} logged in")
    return Token(access_token=access_token, token_type="bearer")


@router.post("/logout", status_code=204)
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
    session: Session = Depends(get_session),  # noqa: B008
) -> None:
    token = credentials.credentials
    try:
        logout_user(token, session)
    except Exception:
        raise InternalServerError()

    logger.info(f"User {current_user.id} logged out")


@router.post("/promote/{username}", response_model=Token)
def promote_user(
    username: str,
    session: Session = Depends(get_session),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
) -> Token:
    if current_user.role != UserRole.admin:
        raise AuthorizationError()

    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise NotFoundError()

    user.role = UserRole.admin
    session.add(user)
    session.commit()
    session.refresh(user)

    access_token = create_access_token(
        {"sub": str(user.id), "role": user.role.value},
        expires_delta=timedelta(minutes=15),
    )

    logger.info(f"User {user.id} promoted to admin by {current_user.id}")
    return Token(access_token=access_token, token_type="bearer")
