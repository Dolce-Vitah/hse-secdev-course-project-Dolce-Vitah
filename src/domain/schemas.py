from pydantic import BaseModel, Field, HttpUrl, constr


class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=100)
    password: constr(min_length=8)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class WishBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    link: HttpUrl | None = None
    price_estimate: float | None = Field(None, ge=0)
    notes: str | None = None

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
