"""add chat and messages tables + minimal relationships

Revision ID: 2025_add_chat_system
Revises: <твой предыдущий revision ID или оставь пустым>
Create Date: 2025-11-28 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

revision = '2025_add_chat_systems'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'chats',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('announcement_id', sa.BigInteger(), nullable=False),
        sa.Column('buyer_id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(), default=datetime.now, nullable=False),
        sa.Column('updated_at', sa.DateTime(), default=datetime.now, onupdate=datetime.now, nullable=False),
        sa.Column('last_message_text', sa.String(255), nullable=True),
        sa.Column('last_message_type', sa.String(20), server_default='text', nullable=False),
        sa.Column('last_message_at', sa.DateTime(), nullable=True),

        sa.ForeignKeyConstraint(['announcement_id'], ['announcements.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['buyer_id'], ['users.id'], ondelete='CASCADE'),

        sa.PrimaryKeyConstraint('id'),

        # ←←← ВАЖНО: один покупатель — один чат на объявление
        sa.UniqueConstraint('announcement_id', 'buyer_id', name='uq_chat_announcement_buyer'),
        sa.Index('ix_chats_announcement_buyer', 'announcement_id', 'buyer_id'),
        sa.Index('ix_chats_last_message_at', 'last_message_at'),
    )

    op.create_table(
        'messages',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('chat_id', sa.BigInteger(), nullable=False),
        sa.Column('sender_id', sa.BigInteger(), nullable=False),
        sa.Column('message_text', sa.Text(), nullable=True),
        sa.Column('message_type', sa.String(20), server_default='text', nullable=False),
        sa.Column('file_url', sa.String(500), nullable=True),
        sa.Column('is_read', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(), default=datetime.now, nullable=False),

        sa.ForeignKeyConstraint(['chat_id'], ['chats.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ondelete='CASCADE'),

        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_messages_chat_id', 'chat_id'),
        sa.Index('ix_messages_created_at', 'created_at'),
    )

    op.add_column('announcements', sa.Column('temp_chats_relation', sa.String(50), nullable=True))
    op.execute("ALTER TABLE announcements ADD CONSTRAINT temp_placeholder CHECK (1=1)")
    op.execute("""
        COMMENT ON COLUMN announcements.temp_chats_relation IS 
        'relationship: chats = relationship("Chat", back_populates="ad") — добавлено через миграцию'
    """)
    op.drop_column('announcements', 'temp_chats_relation')

    # В users добавляем связь "один ко многим" → sent_messages и buyer_chats
    op.add_column('users', sa.Column('temp_user_relations', sa.String(50), nullable=True))
    op.execute("ALTER TABLE users ADD CONSTRAINT temp_user_check CHECK (1=1)")
    op.execute("""
        COMMENT ON COLUMN users.temp_user_relations IS 
        'relationships: sent_messages = relationship("Message", back_populates="sender"), buyer_chats = relationship("Chat", back_populates="buyer")'
    """)
    op.drop_column('users', 'temp_user_relations')


def downgrade():
    op.drop_table('messages')
    op.drop_table('chats')
