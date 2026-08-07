from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.dependencies import get_current_user, get_db, require_role

from models.enums import RoleEnum, StatusEnum
from models.ticket import Ticket
from models.user import User
from schemas.ticket import TicketAssign, TicketCreate, TicketRead

router = APIRouter(tags=["tickets"])

@router.get("/", response_model=list[TicketRead])
def get_tickets(db: Session = Depends(get_db)) -> list[Ticket]:
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

    ticket.assignee_id = assignment.assignee_id
    ticket.assigned_by_id = current_user.id
    ticket.status = StatusEnum.in_progress
    ticket.is_new = False

    db.commit()
    db.refresh(ticket)

    return ticket
