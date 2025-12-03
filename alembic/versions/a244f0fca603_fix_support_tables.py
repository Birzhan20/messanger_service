"""fix support tables

Revision ID: a244f0fca603
Revises: acdfeaca509d
Create Date: 2025-12-03 04:01:23.393685

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a244f0fca603'
down_revision: Union[str, Sequence[str], None] = 'acdfeaca509d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'room',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'))
    )
    op.create_index('ix_room_id', 'room', ['id'], unique=False)

    op.create_table(
        'support_chat',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('room_id', sa.Integer(), sa.ForeignKey('room.id', ondelete='CASCADE')),
        sa.Column('sender', sa.Enum('user', 'assistant', name='sendertype'), nullable=False),
        sa.Column('message', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'))
    )
    op.create_index('ix_support_chat_id', 'support_chat', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_support_chat_id', table_name='support_chat')
    op.drop_table('support_chat')
    op.drop_index('ix_room_id', table_name='room')
    op.drop_table('room')
