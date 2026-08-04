from datetime import date

from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="employee", nullable=False)
    created_at = Column(Date, nullable=False, default=date.today)

    tickets = relationship("Ticket", back_populates="user")
    comments = relationship("Comment", back_populates="user")