from datetime import date

from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    name: str
    email: str
    role: str = "employee"


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserRead(UserBase):
    id: int
    created_at: date | None = None

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    token: str
    user: UserRead
