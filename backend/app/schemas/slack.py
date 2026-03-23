"""Pydantic response schemas for the Slack integration."""

from pydantic import BaseModel


class SlackMessageResponse(BaseModel):
    id: str
    channel: str
    author: str
    text: str
    time: str
    isMention: bool


class SlackFeedResponse(BaseModel):
    messages: list[SlackMessageResponse]
    error: str | None = None
