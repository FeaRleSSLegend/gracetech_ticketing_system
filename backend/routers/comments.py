from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.dependencies import get_current_user, get_db

from models.comment import Comment
from models.ticket import Ticket
from models.user import User
from schemas.comment import CommentCreate, CommentRead

router = APIRouter(tags=["comments"])


@router.get("/{ticket_id}", response_model=list[CommentRead])
def get_comments(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Comment]:
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Ticket not found"},
        )

    return (
        db.query(Comment)
        .filter(Comment.ticket_id == ticket_id)
        .order_by(Comment.created_at.asc())
        .all()
    )


@router.post("/{ticket_id}", response_model=CommentRead)
def create_comment(
    ticket_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Comment:
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Ticket not found"},
        )

    db_comment = Comment(
        ticket_id=ticket_id,
        # Author comes from the session, never from the request body.
        user_id=current_user.id,
        body=comment.body,
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment
