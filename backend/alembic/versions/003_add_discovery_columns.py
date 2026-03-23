"""Add discovery pipeline columns to prospects table.

Revision ID: 003
Revises: 002
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("prospects", sa.Column("source", sa.String(50), server_default="web_search"))
    op.add_column("prospects", sa.Column("discovery_data", JSON, nullable=True))
    op.add_column("prospects", sa.Column("enriched_at", sa.DateTime(timezone=True), nullable=True))

    # Update existing status default from 'scored' to keep them compatible
    op.create_index("ix_prospects_status", "prospects", ["status"])
    op.create_index("ix_prospects_source", "prospects", ["source"])


def downgrade() -> None:
    op.drop_index("ix_prospects_source", table_name="prospects")
    op.drop_index("ix_prospects_status", table_name="prospects")
    op.drop_column("prospects", "enriched_at")
    op.drop_column("prospects", "discovery_data")
    op.drop_column("prospects", "source")
