from base import Base
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime
from enum import Enum

class TicketStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"
    IN_PROGRESS = "in_progress"

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String, nullable=False, default=TicketStatus.OPEN.value)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "message": self.message,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


