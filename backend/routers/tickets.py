from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from core.dependencies import get_current_user, get_db, require_role

from models.enums import NotificationKindEnum, RoleEnum, StatusEnum
from models.notification import Notification
from models.ticket import Ticket
from models.user import User
from schemas.ticket import TicketCreate, TicketRead

router = APIRouter(tags=["tickets"])


def _with_users(query):
    """Eager-load the user relationships TicketRead serializes.

    Without this the schema would lazy-load them one ticket at a time (an N+1),
    and would fail outright if the session were already closed.
    """
    return query.options(
        joinedload(Ticket.creator),
        joinedload(Ticket.assignee),
    )


def _load_ticket(db: Session, ticket_id: int) -> Ticket:
    return _with_users(db.query(Ticket)).filter(Ticket.id == ticket_id).first()


@router.get("/", response_model=list[TicketRead])
def get_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Ticket]:
    return _with_users(db.query(Ticket)).all()


@router.post("/", response_model=TicketRead)
def create_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Ticket:
    db_ticket = Ticket(
        category=ticket.category,
        comment=ticket.comment,
        office=ticket.office,
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

    return _load_ticket(db, db_ticket.id)


@router.post("/{id}/claim", response_model=TicketRead)
def claim_ticket(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.admin)),
) -> Ticket:
    """An admin takes an unclaimed ticket for themselves."""
    ticket = db.query(Ticket).filter(Ticket.id == id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Ticket not found"},
        )

    if ticket.assignee_id is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "This ticket has already been claimed"},
        )

    ticket.assignee_id = current_user.id
    ticket.status = StatusEnum.in_progress
    ticket.is_new = False

    db.commit()
    db.refresh(ticket)

    # Broadcast so the rest of the admins can see the ticket is taken.
    db.add(
        Notification(
            kind=NotificationKindEnum.claimed,
            recipient_id=None,
            actor_id=current_user.id,
            ticket_id=ticket.id,
            category=ticket.category,
            comment=ticket.comment,
        )
    )
    db.commit()

    return _load_ticket(db, ticket.id)
