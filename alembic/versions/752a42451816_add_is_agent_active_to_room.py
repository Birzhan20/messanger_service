"""add is_agent_active to room

Revision ID: 752a42451816
Revises: a244f0fca603
Create Date: 2025-12-10 16:42:06.042303

"""
from alembic import op
import sqlalchemy as sa


revision = 'add_is_agent_active_room'
down_revision = 'a244f0fca603'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('room', sa.Column('is_agent_active', sa.Boolean(), server_default=sa.false(), nullable=False))


def downgrade():
    op.drop_column('room', 'is_agent_active')
