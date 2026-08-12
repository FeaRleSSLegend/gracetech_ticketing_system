from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from models.enums import CategoryEnum, StatusEnum


class TicketCreate(BaseModel):
    category: CategoryEnum
    comment: str


class TicketStatusUpdate(BaseModel):
    status: StatusEnum


class TicketRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: CategoryEnum
    comment: str
    status: StatusEnum
    created_by_id: int
    assignee_id: Optional[int] = None
    assigned_by_id: Optional[int] = None
    is_new: bool
    created_at: datetime
    closed_on: Optional[datetime] = None


class TicketAssign(BaseModel):
    assignee_id: int
