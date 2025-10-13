from datetime import datetime

from sqlmodel import Field, Session, SQLModel, select


class RevokedToken(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    token: str
    revoked_at: datetime = Field(default_factory=datetime.utcnow)


def is_token_revoked(session: Session, token: str) -> bool:
    return (
        session.exec(select(RevokedToken).where(RevokedToken.token == token)).first()
        is not None
    )
