"""add placeholder columns and comments for relationships

Revision ID: 2025_add_chat_system
Revises: 2025_add_chat_columns
Create Date: 2025-11-28 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '2025_add_chat_system'
down_revision = '2025_add_chat_columns'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('announcements', sa.Column('temp_chats_relation', sa.String(50), nullable=True))
    op.execute("ALTER TABLE announcements ADD CONSTRAINT temp_placeholder CHECK (1=1)")
    op.execute("""COMMENT ON COLUMN announcements.temp_chats_relation IS
        'relationship: chats = relationship("Chat", back_populates="ad") — добавлено через миграцию'""")
    op.drop_column('announcements', 'temp_chats_relation')

    op.add_column('users', sa.Column('temp_user_relations', sa.String(50), nullable=True))
    op.execute("ALTER TABLE users ADD CONSTRAINT temp_user_check CHECK (1=1)")
    op.execute("""COMMENT ON COLUMN users.temp_user_relations IS
        'relationships: sent_messages = relationship("Message", back_populates="sender"), buyer_chats = relationship("Chat", back_populates="buyer")'""")
    op.drop_column('users', 'temp_user_relations')


def downgrade():
    pass  
