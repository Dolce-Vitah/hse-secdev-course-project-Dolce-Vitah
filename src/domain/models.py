from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class UserRole(str, Enum):
    user = "user"
    admin = "admin"


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password_hash: str
    role: UserRole = Field(default=UserRole.user)


class Wish(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    link: Optional[str] = None
    price_estimate: Optional[Decimal] = None
    notes: Optional[str] = None
    owner_id: int = Field(foreign_key="user.id")
