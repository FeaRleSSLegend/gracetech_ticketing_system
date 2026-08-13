from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, model_validator

from models.enums import CategoryEnum, StatusEnum


class TicketCreate(BaseModel):
    category: CategoryEnum
    comment: str
    office: str


class TicketStatusUpdate(BaseModel):
    status: StatusEnum


class TicketRead(BaseModel):
    """Frontend-facing view of a ticket.

    createdBy and assignedTo are user *names*, one hop away through the
    relationships, so the raw object is unpacked by the before-validator below.
    office is a plain column and needs no lookup.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    category: CategoryEnum
    comment: str
    office: str
    status: StatusEnum
    createdBy: str
    assignedTo: Optional[str] = None
    isNew: bool
    time: datetime
    closedOn: Optional[datetime] = None

    @model_validator(mode="before")
    @classmethod
    def _from_orm(cls, data: Any) -> Any:
        # Already a plain dict (built by hand, or re-validated): leave it alone.
        if isinstance(data, dict):
            return data

        creator = getattr(data, "creator", None)
        assignee = getattr(data, "assignee", None)
        return {
            "id": data.id,
            "category": data.category,
            "comment": data.comment,
            "office": data.office,
            "status": data.status,
            "createdBy": creator.name if creator is not None else "",
            "assignedTo": assignee.name if assignee is not None else None,
            "isNew": data.is_new,
            "time": data.created_at,
            "closedOn": data.closed_on,
        }
