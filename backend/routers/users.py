from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from core.dependencies import get_db, require_role

from models.comment import Comment
from models.enums import RoleEnum
from models.notification import Notification
from models.ticket import Ticket
from models.user import User
from schemas.user import UserListResponse

router = APIRouter(tags=["users"])


@router.get("/", response_model=UserListResponse)
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.admin)),
) -> UserListResponse:
    """Every employee. Admins are listed by GET /api/admins instead."""
    employees = (
        db.query(User)
        .filter(User.role == RoleEnum.employee)
        .order_by(User.id)
        .all()
    )
    return UserListResponse(users=employees)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.admin)),
) -> Response:
    """Remove an employee account.

    Scoped to employees: an admin id is refused rather than silently deleted
    through the wrong route.
    """
    user = db.query(User).filter(User.id == id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "User not found"},
        )

    if user.role != RoleEnum.employee:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "Use the admins endpoint to remove admin accounts"},
        )

    # tickets.created_by_id is NOT NULL, so this user's tickets would have to be
    # destroyed along with them. Refuse instead, matching DELETE /api/admins/{id}.
    authored = db.query(Ticket).filter(Ticket.created_by_id == user.id).count()
    if authored:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": (
                    f"Cannot delete a user with existing tickets: this user filed "
                    f"{authored} ticket(s). Delete those tickets first."
                )
            },
        )

    # notifications.actor_id is NOT NULL, and a targeted notification with a
    # nulled recipient would silently become a broadcast, so these rows go.
    db.query(Notification).filter(
        (Notification.actor_id == user.id) | (Notification.recipient_id == user.id)
    ).delete(synchronize_session=False)

    # comments.user_id is nullable, so the thread survives without its author.
    db.query(Comment).filter(Comment.user_id == user.id).update(
        {Comment.user_id: None}, synchronize_session=False
    )

    db.delete(user)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
