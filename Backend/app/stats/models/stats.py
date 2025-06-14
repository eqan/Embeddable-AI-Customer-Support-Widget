from sqlalchemy import (
    Column, Integer, Float, DateTime, ForeignKey, UniqueConstraint
)
from datetime import datetime
from base import Base      # your SQLAlchemy Declarative Base

class ConversationStats(Base):
    __tablename__ = "conversation_stats"
    __table_args__ = (
        UniqueConstraint("user_id", name="uix_date_user"),  # optional
    )

    id                            = Column(Integer, primary_key=True)
    user_id                       = Column(Integer, ForeignKey("users.id"), nullable=True)
    conversations                 = Column(Integer, default=0)   # distinct session_ids
    messages                      = Column(Integer, default=0)   # rows in chats
    bookings                      = Column(Integer, default=0)   # sessions where is_booking=True
    human_handoffs                = Column(Integer, default=0)   # sessions where is_human_handoff=True
    successful_conversations      = Column(Integer, default=0)   # bookings  + (convs-handoffs)
    success_rate                  = Column(Float,  default=0.0)  # successful / conversations
    avg_messages_per_conversation = Column(Float,  default=0.0)  # messages   / conversations
    created_at                    = Column(DateTime, default=datetime.utcnow)
    updated_at                    = Column(DateTime, default=datetime.utcnow,
                                           onupdate=datetime.utcnow)