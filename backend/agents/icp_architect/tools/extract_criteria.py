"""Tool that uses Claude to extract structured ICP criteria from conversation."""

import json
import re
from typing import Any

from agents.base.tool import BaseTool


class ExtractCriteriaTool(BaseTool):
    name = "extract_criteria"
    description = "Extract structured ICP criteria from a user's natural-language description."

    async def execute(self, *, message: str, model: str = "claude-sonnet-4-5-20250929") -> dict:
        system_prompt = self.load_prompt("ingestion")

        response = await self.client.messages.create(
            model=model,
            max_tokens=2048,
            system=system_prompt,
            messages=[{"role": "user", "content": message}],
        )

        raw = response.content[0].text
        parsed = self._parse_json(raw)
        return parsed

    @staticmethod
    def _parse_json(text: str) -> dict:
        """Parse JSON from Claude's response, handling optional markdown fences."""
        # Strip markdown code fences if present
        cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip())
        cleaned = re.sub(r"\s*```$", "", cleaned)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {
                "error": "Failed to parse Claude response as JSON",
                "raw_response": text,
            }
