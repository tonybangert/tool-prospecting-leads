"""Claude-powered prospect discovery using Anthropic's web_search tool.

Uses Claude's built-in web search to find LinkedIn profiles matching ICP
criteria, then extracts structured prospect data — all in a single API call.
No external search API keys needed.
"""

import json
import re

import anthropic

from app.config import settings


class ProspectResearcher:
    """Uses Claude + web_search to discover and parse prospect data."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.client = anthropic.AsyncAnthropic(
            api_key=api_key or settings.anthropic_api_key
        )
        self.model = model or settings.claude_model

    async def discover_prospects(self, icp_criteria: dict) -> list[dict]:
        """Search the web for prospects matching ICP criteria and return structured data.

        Claude uses the web_search tool to find LinkedIn profiles, then
        extracts and returns a JSON array of prospect objects.
        """
        prompt = self._build_discovery_prompt(icp_criteria)

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            tools=[{
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": 5,
            }],
            messages=[{"role": "user", "content": prompt}],
        )

        # Handle pause_turn — Claude may need multiple rounds
        while response.stop_reason == "pause_turn":
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                tools=[{
                    "type": "web_search_20250305",
                    "name": "web_search",
                    "max_uses": 5,
                }],
                messages=[
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": response.content},
                    {"role": "user", "content": "Continue."},
                ],
            )

        # Extract the final text block containing JSON
        for block in reversed(response.content):
            if block.type == "text" and block.text.strip():
                return self._parse_response(block.text)

        return []

    @staticmethod
    def _build_discovery_prompt(icp_criteria: dict) -> str:
        """Build the prompt that instructs Claude to search for and extract prospects."""
        criteria_text = json.dumps(icp_criteria, indent=2)

        # Build search guidance from ICP
        search_hints = []
        personas = icp_criteria.get("personas", [])
        if personas:
            titles = [p.get("title", "") for p in personas if p.get("title")]
            if titles:
                search_hints.append(f"Job titles: {', '.join(titles)}")

        industries = icp_criteria.get("industries", [])
        if industries:
            search_hints.append(f"Industries: {', '.join(industries)}")

        geos = icp_criteria.get("geographies", [])
        if geos:
            search_hints.append(f"Locations: {', '.join(geos)}")

        buying_triggers = icp_criteria.get("buying_triggers", [])
        if buying_triggers:
            search_hints.append(f"Buying signals to look for: {', '.join(buying_triggers)}")

        hints_text = "\n".join(f"- {h}" for h in search_hints) if search_hints else "- Use the criteria below"

        return f"""You are a sales research assistant. Your job is to find real people on LinkedIn who match the Ideal Customer Profile below.

## ICP Criteria
{criteria_text}

## Search Guidance
{hints_text}

## Instructions
1. Search for LinkedIn profiles (site:linkedin.com/in/) matching the ICP criteria. Focus on the job titles, industries, and locations specified.
2. Search multiple queries if needed to find diverse results (different title variations, industries, etc.).
3. Prioritize companies showing buying signals listed above (if any) — e.g. companies that recently hired for operations roles, posted AI-related job openings, received funding, or are undergoing tech migrations.
4. From the search results, extract up to 10 real prospects.

After searching, return your findings as ONLY a JSON array (no markdown fences, no extra text before or after the array). Each object must have exactly these fields:
- "first_name": string or null
- "last_name": string or null
- "title": their job title, string or null
- "seniority": one of "entry", "senior", "manager", "director", "vp", "c_suite", "founder", or null
- "company_name": string or null
- "industry": inferred industry, string or null
- "location": string or null
- "linkedin_url": the LinkedIn profile URL
- "icp_fit_summary": 1-sentence explanation of how well they match the ICP

Infer seniority from job title (e.g., "VP of Sales" → "vp", "CTO" → "c_suite", "Director of Engineering" → "director").
If a field cannot be determined from the search results, set it to null."""

    @staticmethod
    def _parse_response(text: str) -> list[dict]:
        """Parse Claude's JSON response, handling optional markdown fences."""
        cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip())
        cleaned = re.sub(r"\s*```$", "", cleaned)

        # Try parsing the whole text as JSON
        try:
            data = json.loads(cleaned)
            return data if isinstance(data, list) else data.get("prospects", [])
        except json.JSONDecodeError:
            pass

        # Fallback: find JSON array in the text
        match = re.search(r"\[.*\]", cleaned, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
                return data if isinstance(data, list) else []
            except json.JSONDecodeError:
                pass

        return []
