from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship

from database import Base
from models.enums import PriorityEnum, CategoryEnum, StatusEnum


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    priority = Column(
        Enum(PriorityEnum, values_callable=lambda x: [e.value for e in x], native_enum=False),
        nullable=False,
    )
    category = Column(
        Enum(CategoryEnum, values_callable=lambda x: [e.value for e in x], native_enum=False),
        nullable=False,
    )
    status = Column(
        Enum(StatusEnum, values_callable=lambda x: [e.value for e in x], native_enum=False),
        nullable=False,
        default=StatusEnum.open,
    )
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    creator = relationship("User", foreign_keys=[created_by], back_populates="tickets_created")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="tickets_assigned")
    comments = relationship("Comment", back_populates="ticket", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="ticket", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Ticket id={self.id} status={self.status}>"