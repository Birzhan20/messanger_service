"""add relationships in models

Revision ID: 2025_add_model_relationships
Revises: 2025_add_chat_columns
Create Date: 2025-11-28 18:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '2025_add_model_relationships'
down_revision = '2025_add_chat_system'
branch_labels = None
depends_on = None


def upgrade():
    pass  # все изменения через модели, колонок не добавляем


def downgrade():
    pass
