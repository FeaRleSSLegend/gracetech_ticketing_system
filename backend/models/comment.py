from sqlalchemy import Column, Integer, String, Date, ForeignKey, Date
from database import Base, engine
from sqlalchemy.orm import relationship

class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey('tickets.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    body = Column(String, nullable=False)
    created_at = Column(Date, nullable=False)

    # Define relationship with Ticket and User models
    ticket = relationship("Ticket", back_populates="comments")
    user = relationship("User", back_populates="comments")
