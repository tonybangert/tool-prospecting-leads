"""Base agent class providing shared infrastructure."""

from typing import Any

import anthropic

from agents.base.tool import BaseTool


class BaseAgent:
    """Base class for all agents.

    Creates an AsyncAnthropic client and provides tool registration.
    Subclasses should instantiate their tools in __init__, passing self.client.
    """

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5-20250929") -> None:
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model
        self.tools: list[BaseTool] = []

    def register_tool(self, tool: BaseTool) -> None:
        self.tools.append(tool)

    def get_tool(self, name: str) -> BaseTool | None:
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None

    async def run(self, **kwargs: Any) -> dict:
        raise NotImplementedError("Subclasses must implement run()")
