from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from database import Base, engine
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default='employee', nullable=False)
    created_at = Column(Date, nullable=False)

    # Define relationship with Ticket model
    tickets = relationship("Ticket", back_populates="user")