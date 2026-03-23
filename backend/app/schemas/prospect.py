"""Pydantic schemas for prospect endpoints."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ProspectResponse(BaseModel):
    id: uuid.UUID
    icp_model_id: uuid.UUID
    apollo_person_id: str | None
    first_name: str | None
    last_name: str | None
    email: str | None
    phone: str | None
    title: str | None
    seniority: str | None
    linkedin_url: str | None
    company_name: str | None
    company_domain: str | None
    industry: str | None
    employee_count: int | None
    company_location: str | None
    icp_fit_score: float | None
    score_breakdown: dict | None
    source: str | None
    discovery_data: dict | None
    enriched_at: datetime | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ProspectListResponse(BaseModel):
    items: list[ProspectResponse]
    total: int


class SearchRequest(BaseModel):
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=25, ge=1, le=100)


class DiscoverRequest(BaseModel):
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=10, ge=1, le=10)


class SelectProspectsRequest(BaseModel):
    prospect_ids: list[uuid.UUID]


class EnrichRequest(BaseModel):
    prospect_ids: list[uuid.UUID]
