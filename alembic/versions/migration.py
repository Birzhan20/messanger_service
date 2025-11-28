"""add new columns and indexes to chats and messages

Revision ID: 2025_add_chat_columns
Revises: 2025_initial
Create Date: 2025-11-28 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

revision = '2025_add_chat_columns'
down_revision = '2025_initial'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('chats', sa.Column('announcement_id', sa.BigInteger(), nullable=False))
    op.add_column('chats', sa.Column('buyer_id', sa.BigInteger(), nullable=False))
    op.add_column('chats', sa.Column('last_message_text', sa.String(255), nullable=True))
    op.add_column('chats', sa.Column('last_message_type', sa.String(20), server_default='text', nullable=False))
    op.add_column('chats', sa.Column('last_message_at', sa.DateTime(), nullable=True))
    op.add_column('chats', sa.Column('created_at', sa.DateTime(), default=datetime.now, nullable=False))
    op.add_column('chats', sa.Column('updated_at', sa.DateTime(), default=datetime.now, onupdate=datetime.now, nullable=False))

    op.create_foreign_key(None, 'chats', 'announcements', ['announcement_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'chats', 'users', ['buyer_id'], ['id'], ondelete='CASCADE')

    op.create_unique_constraint('uq_chat_announcement_buyer', 'chats', ['announcement_id', 'buyer_id'])
    op.create_index('ix_chats_announcement_buyer', 'chats', ['announcement_id', 'buyer_id'])
    op.create_index('ix_chats_last_message_at', 'chats', ['last_message_at'])

    op.add_column('messages', sa.Column('message_type', sa.String(20), server_default='text', nullable=False))
    op.add_column('messages', sa.Column('file_url', sa.String(500), nullable=True))
    op.add_column('messages', sa.Column('is_read', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('messages', sa.Column('created_at', sa.DateTime(), default=datetime.now, nullable=False))
    op.add_column('messages', sa.Column('message_text', sa.Text(), nullable=True))

    op.create_foreign_key(None, 'messages', 'chats', ['chat_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'messages', 'users', ['sender_id'], ['id'], ondelete='CASCADE')
    op.create_index('ix_messages_chat_id', 'messages', ['chat_id'])
    op.create_index('ix_messages_created_at', 'messages', ['created_at'])


def downgrade():
    op.drop_index('ix_messages_created_at', table_name='messages')
    op.drop_index('ix_messages_chat_id', table_name='messages')
    op.drop_constraint(None, 'messages', type_='foreignkey')
    op.drop_constraint(None, 'messages', type_='foreignkey')
    op.drop_column('messages', 'message_text')
    op.drop_column('messages', 'created_at')
    op.drop_column('messages', 'is_read')
    op.drop_column('messages', 'file_url')
    op.drop_column('messages', 'message_type')
    op.drop_column('messages', 'chat_id')

    op.drop_index('ix_chats_last_message_at', table_name='chats')
    op.drop_index('ix_chats_announcement_buyer', table_name='chats')
    op.drop_constraint('uq_chat_announcement_buyer', 'chats', type_='unique')
    op.drop_constraint(None, 'chats', type_='foreignkey')
    op.drop_constraint(None, 'chats', type_='foreignkey')
    op.drop_column('chats', 'updated_at')
    op.drop_column('chats', 'created_at')
    op.drop_column('chats', 'last_message_at')
    op.drop_column('chats', 'last_message_type')
    op.drop_column('chats', 'last_message_text')
    op.drop_column('chats', 'buyer_id')
    op.drop_column('chats', 'announcement_id')
