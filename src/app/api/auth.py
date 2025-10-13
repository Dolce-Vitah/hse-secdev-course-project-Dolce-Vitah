from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select

from src.adapters.database import get_session
from src.app.security import (
    bearer_scheme,
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from src.domain.models import User, UserRole
from src.domain.schemas import Token, UserCreate
from src.shared.errors import (
    AuthenticationError,
    AuthorizationError,
    InternalServerError,
    UserAlreadyExistsError,
)

from ..utils.token_utils import RevokedToken

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token)
def register(user_in: UserCreate, session: Session = Depends(get_session)):
    existing = session.exec(
        select(User).where(User.username == user_in.username)
    ).first()
    if existing:
        raise UserAlreadyExistsError(f"Username '{user_in.username}' already exists")

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
        raise InternalServerError("Failed to create user")

    access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return Token(access_token=access_token, token_type="bearer")


@router.post("/login", response_model=Token)
def login(user_in: UserCreate, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == user_in.username)).first()
    if not user or not verify_password(user_in.password, user.password_hash):
        raise AuthorizationError("Invalid credentials")

    access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return Token(access_token=access_token, token_type="bearer")


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    credentials=Depends(bearer_scheme),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    token = credentials.credentials
    try:
        revoked = RevokedToken(token=token)
        session.add(revoked)
        session.commit()
    except Exception:
        raise InternalServerError("Failed to revoke token")


@router.post("/promote/{username}", response_model=Token)
def promote_user(
    username: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.admin:
        raise AuthorizationError("Only admins can promote users")

    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise AuthenticationError(f"User '{username}' not found")

    user.role = UserRole.admin
    session.add(user)
    session.commit()
    session.refresh(user)

    access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return Token(access_token=access_token, token_type="bearer")
