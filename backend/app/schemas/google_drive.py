"""Pydantic response schemas for Google Drive integration."""

from pydantic import BaseModel


class GoogleDocResponse(BaseModel):
    id: str
    name: str
    mimeType: str
    modifiedTime: str
    modifiedBy: str
    url: str


class GoogleDocTodo(BaseModel):
    text: str
    source: str
    priority: str  # "high" | "medium" | "low"


class GoogleDocAnalysis(BaseModel):
    summary: str = ""
    todos: list[GoogleDocTodo] = []
    correlations: list[str] = []


class GoogleDriveFeedResponse(BaseModel):
    files: list[GoogleDocResponse] = []
    analysis: GoogleDocAnalysis | None = None
    authenticated: bool = False
    authUrl: str | None = None
    error: str | None = None
