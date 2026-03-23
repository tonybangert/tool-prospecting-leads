"""add_phone_to_prospects

Revision ID: 455f5ae0984e
Revises: 003
Create Date: 2026-03-23 15:49:36.611199
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '455f5ae0984e'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("prospects", sa.Column("phone", sa.String(100), nullable=True))


def downgrade() -> None:
    op.drop_column("prospects", "phone")
