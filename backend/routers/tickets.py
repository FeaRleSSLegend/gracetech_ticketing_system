from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.dependencies import get_db

from models.ticket import Ticket
from schemas.ticket import TicketCreate, TicketRead, TicketStatusUpdate, TicketAssign

router = APIRouter(prefix="/api/tickets", tags=["tickets"])

@router.get("/", response_model=list[TicketRead])
def get_tickets(db: Session = Depends(get_db)) -> list[Ticket]:
    tickets = db.query(Ticket).all()
    return tickets

@router.post("/", response_model=TicketRead)
def create_ticket(ticket: TicketCreate, db: Session = Depends(get_db)) -> Ticket:
    db_ticket = Ticket(**ticket.model_dump())
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket



@router.post("/{id}/assign", response_model=dict)
def assign_ticket(
    id: int,
    assignment: TicketAssign,
    db: Session = Depends(get_db),
    # TODO: Replace with proper authentication dependency that extracts user from JWT/session token
    # authorization: str = Header(None)
) -> dict:
    # WARNING: Currently accepting actorRole from request body is a security vulnerability
    # TODO: Extract actual user role from authenticated session/token instead
    # For now, checking the provided actorRole but this should be replaced with:
    # current_user = get_current_user_from_token(authorization)
    # if current_user.role != "admin":
    
    if assignment.actorRole != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "Only admins can assign tickets"}
        )
    
    ticket = db.query(Ticket).filter(Ticket.id == id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Ticket not found"}
        )
    
    ticket.assignedTo = assignment.assigneeName
    ticket.assignedBy = assignment.actorName
    ticket.status = "pending"
    ticket.isNew = False
    
    db.commit()
    db.refresh(ticket)
    
    return {"ticket": ticket}