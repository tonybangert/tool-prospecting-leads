"""Base tool class for agent tools."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import anthropic


class BaseTool(ABC):
    """Abstract base for all agent tools.

    Subclasses receive an AsyncAnthropic client via constructor (DI)
    and must implement execute().
    """

    name: str = ""
    description: str = ""

    def __init__(self, client: anthropic.AsyncAnthropic) -> None:
        self.client = client

    @abstractmethod
    async def execute(self, **kwargs: Any) -> dict:
        ...

    def load_prompt(self, prompt_name: str) -> str:
        """Load a prompt template from the agent's prompts/ directory."""
        prompts_dir = Path(__file__).resolve().parent.parent / self._agent_type / "prompts"
        path = prompts_dir / f"{prompt_name}.txt"
        return path.read_text(encoding="utf-8")

    @property
    def _agent_type(self) -> str:
        """Derive agent type from module path (e.g., 'icp_architect')."""
        module = type(self).__module__  # e.g. agents.icp_architect.tools.extract_criteria
        parts = module.split(".")
        if len(parts) >= 2:
            return parts[1]
        return ""
