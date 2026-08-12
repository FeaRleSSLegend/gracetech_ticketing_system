from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator

from models.enums import RoleEnum


class UserCreate(BaseModel):
    """Signup payload.

    Deliberately has no `role` field: self-registration always produces an
    employee. Admin accounts are created only via POST /api/admins, which is
    gated by require_role(RoleEnum.admin).
    """

    name: str
    email: str
    password: str


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
