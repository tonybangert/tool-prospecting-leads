"""Pydantic schemas for ICP endpoints."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# --- Default scoring weights from architecture doc ---
DEFAULT_SCORING_WEIGHTS: dict = {
    "firmographic_fit": 0.30,
    "tech_fit": 0.20,
    "persona_match": 0.20,
    "timing_signals": 0.15,
    "data_confidence": 0.15,
}


class ICPModelCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    criteria: dict = Field(default_factory=dict)
    scoring_weights: dict = Field(default_factory=lambda: DEFAULT_SCORING_WEIGHTS.copy())


class ICPModelUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    criteria: dict | None = None
    scoring_weights: dict | None = None
    is_active: bool | None = None


class ICPModelResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    criteria: dict
    scoring_weights: dict
    version: str
    is_active: bool
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class ConversationRequest(BaseModel):
    message: str = Field(..., min_length=1)


class ConversationResponse(BaseModel):
    icp_model: ICPModelResponse
    follow_up_questions: list[str] = Field(default_factory=list)
