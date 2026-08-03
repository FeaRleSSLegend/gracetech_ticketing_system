from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict, Field

from models.enums import RoleEnum


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=8)
    role: RoleEnum


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    role: RoleEnum
    created_at: datetime


class TokenResponse(BaseModel):
    token: str
    user: UserRead