from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from database import Base
from models.enums import NotificationKindEnum


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    kind = Column(
        Enum(
            NotificationKindEnum,
            values_callable=lambda x: [e.value for e in x],
            native_enum=False,
        ),
        nullable=False,
    )
    # NULL recipient means "broadcast": visible to every admin.
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    # category and comment are snapshotted at creation time so the row stays
    # readable without joining the ticket.
    category = Column(String, nullable=False)
    comment = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    recipient = relationship("User", foreign_keys=[recipient_id])
    actor = relationship("User", foreign_keys=[actor_id])
    ticket = relationship("Ticket", foreign_keys=[ticket_id])

    def __repr__(self):
        return f"<Notification id={self.id} kind={self.kind} ticket_id={self.ticket_id}>"
