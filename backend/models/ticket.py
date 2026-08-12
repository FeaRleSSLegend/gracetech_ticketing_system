from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from database import Base
from models.enums import CategoryEnum, StatusEnum

from models.attachment import Attachment  # noqa: F401
from models.comment import Comment  # noqa: F401


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(
        Enum(CategoryEnum, values_callable=lambda x: [e.value for e in x], native_enum=False),
        nullable=False,
    )
    comment = Column(Text, nullable=False)
    status = Column(
        Enum(StatusEnum, values_callable=lambda x: [e.value for e in x], native_enum=False),
        nullable=False,
        default=StatusEnum.open,
    )
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_new = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    closed_on = Column(DateTime, nullable=True)

    creator = relationship(
        "User", foreign_keys=[created_by_id], back_populates="tickets_created"
    )
    assignee = relationship(
        "User", foreign_keys=[assignee_id], back_populates="tickets_assigned"
    )
    assigned_by = relationship("User", foreign_keys=[assigned_by_id])
    comments = relationship("Comment", back_populates="ticket")
    attachments = relationship("Attachment", back_populates="ticket")
