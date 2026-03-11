"""ICP Architect agent — orchestrates ICP creation from conversation."""

from agents.base.agent import BaseAgent
from agents.icp_architect.tools.extract_criteria import ExtractCriteriaTool


class ICPArchitect(BaseAgent):
    """Agent that creates and refines ICP models through conversation with Claude."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5-20250929") -> None:
        super().__init__(api_key=api_key, model=model)
        # Inject client into tools at construction time (DI)
        extract_tool = ExtractCriteriaTool(client=self.client)
        self.register_tool(extract_tool)

    async def run(self, *, message: str) -> dict:
        """Process a user message and return structured ICP data."""
        extract_tool = self.get_tool("extract_criteria")
        result = await extract_tool.execute(message=message, model=self.model)
        return result
