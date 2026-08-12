from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.dependencies import get_current_user, get_db, require_role

from models.enums import NotificationKindEnum, RoleEnum, StatusEnum
from models.notification import Notification
from models.ticket import Ticket
from models.user import User
from schemas.ticket import TicketAssign, TicketCreate, TicketRead

router = APIRouter(tags=["tickets"])

@router.get("/", response_model=list[TicketRead])
def get_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Ticket]:
    tickets = db.query(Ticket).all()
    return tickets

@router.post("/", response_model=TicketRead)
def create_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Ticket:
    db_ticket = Ticket(
        category=ticket.category,
        comment=ticket.comment,
        created_by_id=current_user.id,
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)

    # Broadcast to all admins: recipient_id stays NULL.
    db.add(
        Notification(
            kind=NotificationKindEnum.new_ticket,
            recipient_id=None,
            actor_id=current_user.id,
            ticket_id=db_ticket.id,
            category=db_ticket.category,
            comment=db_ticket.comment,
        )
    )
    db.commit()

    return db_ticket



@router.post("/{id}/assign", response_model=TicketRead)
def assign_ticket(
    id: int,
    assignment: TicketAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.admin)),
) -> Ticket:
    ticket = db.query(Ticket).filter(Ticket.id == id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Ticket not found"}
        )

    assignee = db.get(User, assignment.assignee_id)
    if assignee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Assignee not found"}
        )

    ticket.assignee_id = assignment.assignee_id
    ticket.assigned_by_id = current_user.id
    ticket.status = StatusEnum.in_progress
    ticket.is_new = False

    db.commit()
    db.refresh(ticket)

    # Directed at the assignee; the actor is the admin doing the assigning.
    db.add(
        Notification(
            kind=NotificationKindEnum.assigned,
            recipient_id=ticket.assignee_id,
            actor_id=current_user.id,
            ticket_id=ticket.id,
            category=ticket.category,
            comment=ticket.comment,
        )
    )
    db.commit()

    return ticket
