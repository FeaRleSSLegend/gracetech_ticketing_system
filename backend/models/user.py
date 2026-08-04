from datetime import datetime, timezone

from sqlalchemy import Column, Enum, Integer, String, DateTime
from sqlalchemy.orm import relationship

from database import Base
from models.enums import RoleEnum


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(
        Enum(RoleEnum, values_callable=lambda x: [e.value for e in x], native_enum=False),
        nullable=False,
    )
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    tickets_created = relationship(
        "Ticket", foreign_keys="Ticket.created_by", back_populates="creator"
    )
    tickets_assigned = relationship(
        "Ticket", foreign_keys="Ticket.assignee_id", back_populates="assignee"
    )
    comments = relationship("Comment", back_populates="user")

    def __repr__(self):
        return f"<User id={self.id} email={self.email!r}>"
