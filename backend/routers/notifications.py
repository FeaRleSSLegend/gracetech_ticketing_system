from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.dependencies import get_current_user, get_db

from models.enums import RoleEnum
from models.notification import Notification
from models.user import User
from schemas.notification import NotificationListResponse, NotificationRead

router = APIRouter(tags=["notifications"])


@router.get("/", response_model=NotificationListResponse)
def get_notifications(
    name: str = Query(..., description="Name of the admin whose notifications to fetch"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NotificationListResponse:
    admin = (
        db.query(User)
        .filter(User.name == name, User.role == RoleEnum.admin)
        .first()
    )
    if admin is None:
        return NotificationListResponse(notifications=[])

    notifications = (
        db.query(Notification)
        .filter(
            (Notification.recipient_id.is_(None))
            | (Notification.recipient_id == admin.id)
        )
        .order_by(Notification.created_at.desc())
        .all()
    )

    return NotificationListResponse(
        notifications=[NotificationRead.model_validate(n) for n in notifications]
    )
