import re

from pydantic import BaseModel, Field, HttpUrl, constr, field_validator


class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=100)
    password: constr(min_length=8)

    @field_validator("username")
    def username_valid(cls, v):
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Username can contain only letters, digits, '-' and '_'")
        return v

    @field_validator("password")
    def password_complexity(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*()_+=\-{}[\]|:;\"'<>,.?/]", v):
            raise ValueError("Password must contain at least one special character")
        return v


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class WishBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    link: HttpUrl | None = None
    price_estimate: float | None = Field(None, ge=0)
    notes: str | None = None

    @field_validator("link")
    def link_safe(cls, v):
        if v is None:
            return v
        if ".." in v.path or "\\" in v.path:
            raise ValueError("Link contains forbidden path traversal sequence")
        return v

    class Config:
        extra = "forbid"


class WishCreate(WishBase):
    pass


class WishUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    link: HttpUrl | None = None
    price_estimate: float | None = Field(None, ge=0)
    notes: str | None = None

    class Config:
        extra = "forbid"


class WishRead(WishBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True
