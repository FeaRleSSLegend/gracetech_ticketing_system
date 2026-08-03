from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, Date
from database import Base, engine
from sqlalchemy.orm import relationship

class Ticket(Base):
    __tablename__ = 'tickets'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(String, default='open', nullable=False)
    category = Column(String, default='medium', nullable=False)
    created_by = Column(String, nullable=False)
    assigned_id = Column(String, ForeignKey('users.id'))
    created_at = Column(Date, nullable=False, default= Date.now())
    updated_at = Column(Date, ForeignKey('users.id'), nullable=False, default= Date.now())

    # Define relationship with User model
    user = relationship("User", back_populates="tickets")
