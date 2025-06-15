from stats.models.stats import ConversationStats
from config.config import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from chatbot.models.chat import Chat
from datetime import datetime
import ast

class StatsService:
    """Service providing conversation statistics for a given user."""
    def __init__(self):
        self.db = Session()

    async def generate_stats(self, user_id: int):
        try:
            chats = self.db.query(Chat).filter(Chat.user_id == user_id).all()
            stats = ConversationStats(user_id=user_id)
            stats.conversations = len(chats)

            # Total number of *user* messages across all conversations
            stats.messages = sum(self.count_user_messages(chat.chat_history) for chat in chats)

            # A booking / hand-off occurs when **any** model message inside the
            # history has the corresponding boolean flag set to ``True``.
            stats.bookings = sum(
                1 for chat in chats if self._has_flag(self._parse_chat_history(chat.chat_history), "is_booking")
            )
            stats.human_handoffs = sum(
                1 for chat in chats if self._has_flag(self._parse_chat_history(chat.chat_history), "is_human_handoff")
            )
            stats.successful_conversations = stats.bookings + (stats.conversations - stats.human_handoffs)

            # Protect against division by zero.
            if stats.conversations:
                stats.success_rate = stats.successful_conversations / stats.conversations
                stats.avg_messages_per_conversation = stats.messages / stats.conversations
            else:
                stats.success_rate = 0.0
                stats.avg_messages_per_conversation = 0.0

            stats.created_at = datetime.now()
            stats.updated_at = datetime.now()
            print(stats)

            # Add or update operation
            existing_stats = self.db.query(ConversationStats).filter(ConversationStats.user_id == user_id).first()
            if existing_stats:
                existing_stats.conversations = stats.conversations
                existing_stats.messages = stats.messages
                existing_stats.bookings = stats.bookings
                existing_stats.human_handoffs = stats.human_handoffs
                existing_stats.successful_conversations = stats.successful_conversations
                existing_stats.success_rate = stats.success_rate
                existing_stats.avg_messages_per_conversation = stats.avg_messages_per_conversation
                existing_stats.updated_at = datetime.now()
            else:
                self.db.add(stats)
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            self.db.close()
            return stats

    async def get_stats(self, user_id: int):
        try:
            stats = self.db.query(ConversationStats).filter(ConversationStats.user_id == user_id).first()
            return stats
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def _parse_chat_history(chat_history_str: str):
        """Safely load ``chat_history_str`` into a Python list.

        The column is currently stored as a *stringified* Python list that uses
        single-quoted keys/values, which is **not** valid JSON.  We therefore first
        attempt ``ast.literal_eval``.  If that fails, we fall back to
        ``json.loads`` which will correctly parse real JSON strings (double quoted
        keys/values).

        A 100 % valid return value is *always* a list – an empty list is returned
        for any malformed payloads.
        """

        # 1. Try ``ast.literal_eval`` for the typical single-quoted representation.
        try:
            history = ast.literal_eval(chat_history_str)
        except (SyntaxError, ValueError):
            # 2. Fall back to proper JSON.
            import json
            try:
                history = json.loads(chat_history_str)
            except (TypeError, json.JSONDecodeError):
                return []  # completely unparseable – treat as empty

        # 3. Guard against bad data
        return history if isinstance(history, list) else []

    @staticmethod
    def _has_flag(history: list[dict], flag: str) -> bool:
        """Return ``True`` if *any* *model* message has ``flag`` set to ``True``."""

        for msg in history:
            if (
                isinstance(msg, dict)
                and msg.get("role") == "model"
                and msg.get(flag) is True
            ):
                return True
        return False

    @staticmethod
    def count_user_messages(chat_history_str: str) -> int:
        """Count *user* messages in ``chat_history_str``."""

        history = StatsService._parse_chat_history(chat_history_str)
        return sum(
            1 for msg in history if isinstance(msg, dict) and msg.get("role") == "user"
        )