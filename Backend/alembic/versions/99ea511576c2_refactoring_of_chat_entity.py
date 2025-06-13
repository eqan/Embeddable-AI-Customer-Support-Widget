"""Refactoring of Chat Entity

Revision ID: 99ea511576c2
Revises: 
Create Date: 2025-06-14 03:13:59.258053

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '99ea511576c2'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('chats', 'response', new_column_name='chat_history')
    pass


def downgrade() -> None:
    op.alter_column('chats', 'chat_history', new_column_name='response')
    pass
