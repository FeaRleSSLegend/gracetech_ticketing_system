from datetime import date

from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base

from models.attachment import Attachment  # noqa: F401
from models.comment import Comment  # noqa: F401


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(String, default="open", nullable=False)
    category = Column(String, default="medium", nullable=False)
    created_by = Column(String, nullable=False)
    assigned_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(Date, nullable=False, default=date.today)
    updated_at = Column(Date, nullable=False, default=date.today)

    user = relationship("User", back_populates="tickets")
    comments = relationship("Comment", back_populates="ticket")
    attachments = relationship("Attachment", back_populates="tickets")
