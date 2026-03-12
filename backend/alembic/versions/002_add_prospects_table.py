"""Add prospects table.

Revision ID: 002
Revises: 001
Create Date: 2026-03-11
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "prospects",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "icp_model_id",
            UUID(as_uuid=True),
            sa.ForeignKey("icp_models.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("apollo_person_id", sa.String(255), nullable=True),
        sa.Column("first_name", sa.String(255), nullable=True),
        sa.Column("last_name", sa.String(255), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("title", sa.String(500), nullable=True),
        sa.Column("seniority", sa.String(100), nullable=True),
        sa.Column("linkedin_url", sa.Text, nullable=True),
        sa.Column("company_name", sa.String(500), nullable=True),
        sa.Column("company_domain", sa.String(255), nullable=True),
        sa.Column("industry", sa.String(255), nullable=True),
        sa.Column("employee_count", sa.Integer, nullable=True),
        sa.Column("company_location", sa.String(500), nullable=True),
        sa.Column("icp_fit_score", sa.Float, nullable=True),
        sa.Column("score_breakdown", sa.JSON, nullable=True),
        sa.Column("apollo_data", sa.JSON, nullable=True),
        sa.Column("status", sa.String(50), server_default="scored"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_prospects_icp_model_id", "prospects", ["icp_model_id"])
    op.create_index("ix_prospects_apollo_person_id", "prospects", ["apollo_person_id"])


def downgrade() -> None:
    op.drop_index("ix_prospects_apollo_person_id", table_name="prospects")
    op.drop_index("ix_prospects_icp_model_id", table_name="prospects")
    op.drop_table("prospects")
