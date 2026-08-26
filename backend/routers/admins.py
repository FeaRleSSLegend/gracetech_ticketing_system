from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.dependencies import get_current_user, get_db, require_role
from core.security import hash_password

from models.comment import Comment
from models.enums import RoleEnum, StatusEnum
from models.notification import Notification
from models.ticket import Ticket
from models.user import User
from schemas.admin import AdminCreate, AdminRead

router = APIRouter(tags=["admins"])


@router.get("/", response_model=list[AdminRead])
def get_admins(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[User]:
    return db.query(User).filter(User.role == RoleEnum.admin).all()


@router.post("/", response_model=AdminRead)
def create_admin(
    admin_create: AdminCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.admin)),
) -> User:
    existing_admin = db.query(User).filter(User.email == admin_create.email).first()
    if existing_admin is not None:
        raise HTTPException(status_code=400, detail="Email already registered")

    admin = User(
        name=admin_create.name,
        email=admin_create.email,
        password_hash=hash_password(admin_create.password),
        # Role is forced server-side; this endpoint only ever mints admins.
        role=RoleEnum.admin,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@router.delete("/{id}")
def delete_admin(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.admin)),
) -> dict:
    """Remove another admin account.

    Their traces have to go somewhere first: four tables carry a foreign key to
    users, two of them NOT NULL, so a bare delete would fail at the database.
    See the detach steps below.
    """
    admin = db.query(User).filter(User.id == id, User.role == RoleEnum.admin).first()
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Admin not found"},
        )

    if admin.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "You cannot remove your own admin account"},
        )

    remaining = db.query(User).filter(User.role == RoleEnum.admin).count()
    if remaining <= 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "Cannot remove the last remaining admin"},
        )

    # tickets.created_by_id is NOT NULL, so a ticket this admin filed themselves
    # would have to be deleted along with them. Refuse instead of destroying it.
    authored = db.query(Ticket).filter(Ticket.created_by_id == admin.id).count()
    if authored:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": (
                    f"This admin filed {authored} ticket(s) and cannot be removed. "
                    "Reassign or delete those tickets first."
                )
            },
        )

    # Release anything they had claimed back into the open pool.
    released = 0
    for ticket in db.query(Ticket).filter(Ticket.assignee_id == admin.id).all():
        ticket.assignee_id = None
        if ticket.status == StatusEnum.in_progress:
            ticket.status = StatusEnum.open
        released += 1

    # notifications.actor_id is NOT NULL and a targeted notification with no
    # recipient would silently become a broadcast, so these rows go.
    db.query(Notification).filter(
        (Notification.actor_id == admin.id) | (Notification.recipient_id == admin.id)
    ).delete(synchronize_session=False)

    # comments.user_id is nullable, so the thread survives without the author.
    db.query(Comment).filter(Comment.user_id == admin.id).update(
        {Comment.user_id: None}, synchronize_session=False
    )

    removed = {"id": admin.id, "name": admin.name, "email": admin.email}
    db.delete(admin)
    db.commit()

    return {"detail": "Admin removed", "admin": removed, "ticketsReleased": released}
