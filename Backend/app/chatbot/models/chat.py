from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from base import Base

class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    chat_history = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "message": self.message,
            "response": self.response,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }