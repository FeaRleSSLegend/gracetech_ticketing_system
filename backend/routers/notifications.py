from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from core.dependencies import get_current_user, get_db

from models.notification import Notification
from models.user import User
from schemas.notification import NotificationListResponse, NotificationRead

router = APIRouter(tags=["notifications"])


@router.get("/", response_model=NotificationListResponse)
def get_notifications(
    name: str = Query(..., description="Name of the user whose notifications to fetch"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NotificationListResponse:
    # Any user, not just admins: resolved/closed notifications target the
    # employee who created the ticket.
    user = db.query(User).filter(User.name == name).first()
    if user is None:
        return NotificationListResponse(notifications=[])

    notifications = (
        db.query(Notification)
        .options(
            joinedload(Notification.recipient),
            joinedload(Notification.actor),
        )
        .filter(
            (Notification.recipient_id.is_(None))
            | (Notification.recipient_id == user.id)
        )
        .order_by(Notification.created_at.desc())
        .all()
    )

    return NotificationListResponse(
        notifications=[NotificationRead.model_validate(n) for n in notifications]
    )
