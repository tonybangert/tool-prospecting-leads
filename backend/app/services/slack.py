"""Slack integration service — fetches channels, messages, and user info."""

import re
from datetime import datetime, timezone

from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError


class SlackService:
    def __init__(self, bot_token: str, user_id: str = ""):
        self.client = AsyncWebClient(token=bot_token)
        self.user_id = user_id
        self._user_cache: dict[str, str] = {}

    async def get_channels(self) -> list[dict]:
        """Return [{id, name}] for all non-archived channels the bot can see."""
        resp = await self.client.conversations_list(
            types="public_channel",
            exclude_archived=True,
            limit=200,
        )
        return [
            {"id": ch["id"], "name": ch["name"]}
            for ch in resp.get("channels", [])
        ]

    async def get_channel_messages(self, channel_id: str, limit: int = 20) -> list[dict]:
        """Return raw messages from a single channel."""
        resp = await self.client.conversations_history(
            channel=channel_id, limit=limit
        )
        return resp.get("messages", [])

    async def get_user_name(self, user_id: str) -> str:
        """Resolve a Slack user ID to a display name, with caching."""
        if user_id in self._user_cache:
            return self._user_cache[user_id]
        try:
            resp = await self.client.users_info(user=user_id)
            profile = resp["user"].get("profile", {})
            name = (
                profile.get("display_name")
                or profile.get("real_name")
                or resp["user"].get("name", user_id)
            )
            self._user_cache[user_id] = name
            return name
        except SlackApiError:
            self._user_cache[user_id] = user_id
            return user_id

    async def get_dashboard_messages(self, limit: int = 20) -> list[dict]:
        """Fetch recent messages across all channels, normalized for the dashboard."""
        channels = await self.get_channels()

        all_messages: list[dict] = []
        per_channel = max(5, limit // max(len(channels), 1))

        for ch in channels:
            try:
                await self.client.conversations_join(channel=ch["id"])
            except SlackApiError:
                pass
            try:
                raw_msgs = await self.get_channel_messages(ch["id"], limit=per_channel)
            except SlackApiError:
                continue

            for msg in raw_msgs:
                if msg.get("subtype") in ("channel_join", "channel_leave", "bot_message"):
                    continue
                if not msg.get("text", "").strip():
                    continue

                user_id = msg.get("user", "")
                author = await self.get_user_name(user_id) if user_id else "Unknown"

                is_mention = bool(
                    self.user_id and re.search(rf"<@{re.escape(self.user_id)}>", msg.get("text", ""))
                )

                cleaned_text = await self._clean_text(msg.get("text", ""))
                time_str = self._format_ts(msg.get("ts", "0"))

                all_messages.append({
                    "id": msg["ts"],
                    "channel": f"#{ch['name']}",
                    "author": author,
                    "text": cleaned_text,
                    "time": time_str,
                    "isMention": is_mention,
                })

        all_messages.sort(key=lambda m: m["id"], reverse=True)
        return all_messages[:limit]

    async def _clean_text(self, text: str) -> str:
        """Replace Slack markup with readable text.

        Slack encodes rich content with angle-bracket patterns:
          - <@U123ABC> → user mention
          - <#C123ABC|channel-name> → channel link
          - <https://example.com|label> → URL with display label
          - <https://example.com> → bare URL
        """
        # Step 1: Resolve user mentions <@USERID>
        user_ids = re.findall(r"<@(U[A-Z0-9]+)>", text)
        for uid in set(user_ids):
            name = await self.get_user_name(uid)
            text = text.replace(f"<@{uid}>", f"@{name}")

        # Step 2: Channel links <#CID|name> → #name
        text = re.sub(r"<#C[A-Z0-9]+\|([^>]+)>", r"#\1", text)

        # Step 3: Labeled URLs <url|label> → label
        text = re.sub(r"<(https?://[^|>]+)\|([^>]+)>", r"\2", text)

        # Step 4: Bare URLs <url> → url
        text = re.sub(r"<(https?://[^>]+)>", r"\1", text)

        return text

    @staticmethod
    def _format_ts(ts: str) -> str:
        """Convert a Slack timestamp like '1711234567.000100' to '8:55 AM'."""
        try:
            dt = datetime.fromtimestamp(float(ts), tz=timezone.utc)
            # %#I works on Windows, %-I on Unix — fall back to lstrip
            return dt.strftime("%I:%M %p").lstrip("0")
        except (ValueError, OSError):
            return ""
