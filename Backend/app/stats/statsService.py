from stats.models.stats import ConversationStats
from config.config import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from chatbot.models.chat import Chat
from datetime import datetime
import ast

async def generate_stats(user_id: int):
    db = Session()
    try:
        chats = db.query(Chat).filter(Chat.user_id == user_id).all()
        stats = ConversationStats(user_id=user_id)
        stats.conversations = len(chats)

        stats.messages = sum(count_user_messages(chat.chat_history) for chat in chats)

        stats.bookings = sum(chat.is_booking for chat in chats)
        stats.human_handoffs = sum(chat.is_human_handoff for chat in chats)
        stats.successful_conversations = stats.bookings + (stats.conversations - stats.human_handoffs)
        stats.success_rate = stats.successful_conversations / stats.conversations
        stats.avg_messages_per_conversation = stats.messages / stats.conversations
        stats.created_at = datetime.now()
        stats.updated_at = datetime.now()
        print(stats)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

def count_user_messages(chat_history_str: str) -> int:
    """
    chat_history_str is something like
    "[{'role': 'user', 'content': 'Hi', ...}, {'role': 'model', ...}]"
    """
    # 1. Safely convert the single-quoted representation to Python objects
    try:
        history = ast.literal_eval(chat_history_str)
    except (SyntaxError, ValueError):
        # fall back if someone already stored valid JSON
        import json
        history = json.loads(chat_history_str)

    # 2. Guard against bad data
    if not isinstance(history, list):
        return 0

    # 3. Count only the messages where role == "user"
    return sum(1 for msg in history if isinstance(msg, dict) and msg.get("role") == "user")