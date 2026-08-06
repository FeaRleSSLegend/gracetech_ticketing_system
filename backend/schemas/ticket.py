from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from models.enums import PriorityEnum, CategoryEnum, StatusEnum


class TicketCreate(BaseModel):
    title: str
    description: str
    status: StatusEnum = "open  "
    category: CategoryEnum


class TicketStatusUpdate(BaseModel):
    status: StatusEnum


class TicketRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    priority: PriorityEnum
    category: CategoryEnum
    status: StatusEnum
    created_by: int
    assignee_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

class TicketAssign(BaseModel):
    assigneeName: str
    actorName: str
    actorRole: str