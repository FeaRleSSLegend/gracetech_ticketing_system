from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, model_validator

from models.enums import NotificationKindEnum


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    kind: NotificationKindEnum
    recipientName: Optional[str] = None
    actorName: str
    ticketId: int
    category: str
    comment: str
    time: datetime

    @model_validator(mode="before")
    @classmethod
    def _from_orm(cls, data: Any) -> Any:
        # Already a plain dict (e.g. built by hand or re-validated): leave it alone.
        if isinstance(data, dict):
            return data

        recipient = getattr(data, "recipient", None)
        actor = getattr(data, "actor", None)
        return {
            "id": data.id,
            "kind": data.kind,
            "recipientName": recipient.name if recipient is not None else None,
            "actorName": actor.name if actor is not None else "",
            "ticketId": data.ticket_id,
            "category": data.category,
            "comment": data.comment,
            "time": data.created_at,
        }


class NotificationListResponse(BaseModel):
    notifications: list[NotificationRead]
