from sqlalchemy import Column, Integer, String, ForeignKey, Date
from database import Base, engine
from sqlalchemy.orm import relationship

class Attachment(Base):
    __tablename__ = 'attachments'

    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey('tickets.id'))
    file_url = Column(String, nullable=False)
    updated_at = Column(Date, nullable=False)

    # Define relationship with tickets
    tickets = relationship("Ticket", back_populates="attachments")

    def __init__(self, path, task_id):
        self.path = path
        self.task_id = task_id

    def __repr__(self):
        return '<Attachment %r>' % self.path


