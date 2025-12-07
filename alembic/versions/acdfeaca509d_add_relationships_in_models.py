"""add relationships in models

Revision ID: acdfeaca509d
Revises: 2025_add_model_relationships
Create Date: 2025-11-28 23:55:40.313082

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'acdfeaca509d'
down_revision: Union[str, Sequence[str], None] = '2025_add_model_relationships'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
