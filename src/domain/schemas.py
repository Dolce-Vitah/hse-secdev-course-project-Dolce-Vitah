import re
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8)

    @field_validator("username")
    def username_valid(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                "Username can contain only " "letters, digits, '-' and '_'"
            )
        return v

    @field_validator("password")
    def password_complexity(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least " "one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least " "one lowercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*()_+=\-{}[\]|:;\"'<>,.?/]", v):
            raise ValueError("Password must contain at least " "one special character")
        return v


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class WishBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    link: Optional[HttpUrl] = None
    price_estimate: Decimal | None = Field(None, ge=0)
    notes: str | None = None

    @field_validator("title", "notes", mode="before")
    def trim_strings(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("link")
    def link_safe(cls, v: Optional[HttpUrl]) -> Optional[HttpUrl]:
        if v is None:
            return None

        path = str(v.path)
        if ".." in path or "\\" in path:
            raise ValueError("Link contains forbidden path traversal sequence")
        return v

    class Config:
        extra = "forbid"


class WishCreate(WishBase):
    pass


class WishUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    link: HttpUrl | None = None
    price_estimate: Decimal | None = Field(None, ge=0)
    notes: str | None = None

    @field_validator("title", "notes", mode="before")
    def trim_optional_strings(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip()
        return v

    class Config:
        extra = "forbid"


class WishRead(WishBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True
        json_encoders = {Decimal: float}
