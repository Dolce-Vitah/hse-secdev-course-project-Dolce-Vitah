import os
from datetime import datetime, timedelta
from typing import cast

from sqlmodel import Field, Session, SQLModel, select
from sqlmodel.sql.expression import ColumnElement


class RevokedToken(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    token: str
    revoked_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime | None = None


def revoke_token(session: Session, token: str, exp: datetime | None = None) -> None:
    revoked = RevokedToken(token=token, expires_at=exp)
    session.add(revoked)
    session.commit()


def is_token_revoked(session: Session, token: str) -> bool:
    return (
        session.exec(select(RevokedToken).where(RevokedToken.token == token)).first()
        is not None
    )


def cleanup_expired_tokens(session: Session) -> None:
    now = datetime.utcnow()
    expired_tokens = session.exec(
        select(RevokedToken).where(cast(ColumnElement, RevokedToken.expires_at) < now)
    ).all()
    for token in expired_tokens:
        session.delete(token)
    if expired_tokens:
        session.commit()


def rotate_secret_if_needed() -> None:
    if os.getenv("JWT_ROTATE_KEY", "false").lower() == "true":
        new_key = f"{os.urandom(32).hex()}-{datetime.utcnow().timestamp()}"
        os.environ["SECRET_KEY"] = new_key


def get_token_expiration(minutes: int = 60) -> datetime:
    return datetime.utcnow() + timedelta(minutes=minutes)
