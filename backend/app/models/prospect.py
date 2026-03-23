"""Prospect database model — stores leads from discovery and enrichment pipeline."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Prospect(Base):
    __tablename__ = "prospects"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    icp_model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("icp_models.id", ondelete="CASCADE"),
        nullable=False,
    )
    apollo_person_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(100), nullable=True)
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    seniority: Mapped[str | None] = mapped_column(String(100), nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    company_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    company_domain: Mapped[str | None] = mapped_column(String(255), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(255), nullable=True)
    employee_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    company_location: Mapped[str | None] = mapped_column(String(500), nullable=True)
    icp_fit_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_breakdown: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    apollo_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    source: Mapped[str] = mapped_column(String(50), default="web_search")
    discovery_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    enriched_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(String(50), default="discovered", index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
