"""add_user_id

Revision ID: e2960de8a277
Revises: 4421e863375f
Create Date: 2025-06-26 21:53:05.436063

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e2960de8a277'
down_revision: Union[str, None] = '4421e863375f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('videos',sa.Column('user_id', sa.Integer(), nullable=False))


def downgrade() -> None:
    op.drop_column('videos', 'user_id')
