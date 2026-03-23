"""Slack API route — serves dashboard messages from the Slack workspace."""

from fastapi import APIRouter

from app.config import settings
from app.schemas.slack import SlackFeedResponse
from app.services.slack import SlackService

router = APIRouter(prefix="/api/slack", tags=["slack"])


@router.get("/messages", response_model=SlackFeedResponse)
async def get_slack_messages():
    if not settings.slack_bot_token:
        return SlackFeedResponse(messages=[], error="Slack not configured")

    try:
        svc = SlackService(
            bot_token=settings.slack_bot_token,
            user_id=settings.slack_user_id,
        )
        messages = await svc.get_dashboard_messages(limit=20)
        return SlackFeedResponse(messages=messages)
    except Exception as exc:
        return SlackFeedResponse(messages=[], error=str(exc))
