from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator

from models.enums import RoleEnum


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: RoleEnum = RoleEnum.employee


class UserLogin(BaseModel):
    email: str
    password: str


class UserRead(BaseModel):
    """Public view of a user. Deliberately excludes password_hash."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: str
    role: RoleEnum

    @field_validator("id", mode="before")
    @classmethod
    def _id_to_str(cls, value: Any) -> Any:
        # The column is an int; the frontend contract wants a string.
        return str(value) if value is not None else value


class AuthResponse(BaseModel):
    user: UserRead
    token: str
