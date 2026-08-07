from datetime import date

from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"))
    file_url = Column(String, nullable=False)
    updated_at = Column(Date, nullable=False, default=date.today)

    ticket = relationship("Ticket", back_populates="attachments")
