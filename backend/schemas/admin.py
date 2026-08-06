from datetime import date

from pydantic import BaseModel, ConfigDict

class AdminBase(BaseModel):
    name: str
    email: str
    role: str = "admin"

class AdminCreate(AdminBase):
    password: str

class AdminRead(AdminBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: date
    updated_at: date