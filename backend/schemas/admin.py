from datetime import datetime

from pydantic import BaseModel, ConfigDict

from models.enums import RoleEnum


class AdminBase(BaseModel):
    name: str
    email: str
    role: RoleEnum = RoleEnum.admin


class AdminCreate(AdminBase):
    password: str


class AdminRead(AdminBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
