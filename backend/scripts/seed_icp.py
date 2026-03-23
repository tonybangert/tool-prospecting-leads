"""Seed the PerformanceLabs / Aplora ICP model into the database.

Usage:
    cd backend && python -m scripts.seed_icp

Safe to re-run — upserts by name.
"""

import asyncio
import sys
from pathlib import Path

# Ensure the backend package is importable when run as a script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from app.database import async_session, engine, Base
from app.models.icp import ICPModel
from app.schemas.icp import DEFAULT_SCORING_WEIGHTS


def build_icp_data() -> dict:
    """Return the full PerformanceLabs / Aplora ICP definition."""
    return {
        "name": "PerformanceLabs / Aplora — Operations Leaders",
        "description": (
            "Mid-market companies with manual or fragmented operational workflows, "
            "where leadership is under pressure to modernize and scale."
        ),
        "criteria": {
            "industries": [
                "SaaS",
                "Technology",
                "Professional Services",
                "Financial Services",
                "Healthcare",
                "Manufacturing",
            ],
            "employee_range": {"min": 100, "max": 2500},
            "revenue_range": {"min": 10_000_000, "max": 500_000_000},
            "geographies": ["United States", "Canada", "United Kingdom"],
            "technologies": [
                "Salesforce",
                "HubSpot",
                "Slack",
                "Jira",
                "Monday.com",
                "Asana",
                "Zapier",
            ],
            "personas": [
                {"title": "CEO", "seniority": "C-level", "context": "Economic buyer — board pressure when revenue grows but EBITDA doesn't follow"},
                {"title": "COO", "seniority": "C-level", "context": "Power sponsor — blindsided by conflicting data, needs unified operational picture"},
                {"title": "CRO", "seniority": "C-level", "context": "Revenue owner — needs attribution-to-revenue visibility across the full GTM funnel"},
            ],
            "pain_points": [
                "Manual data entry across multiple systems",
                "Lack of visibility into cross-team workflows",
                "Difficulty scaling operations without adding headcount",
                "Slow reporting cycles and stale dashboards",
                "Integration gaps between CRM, PM, and finance tools",
            ],
            "buying_triggers": [
                "recently hired a VP/Director of Operations",
                "job postings mentioning AI or automation",
                "series B or later funding round",
                "new CEO or COO in the last 12 months",
                "mentioned digital transformation in earnings call or press",
                "expanding to new markets or geographies",
                "post-acquisition integration underway",
            ],
            "keywords": [
                "operational efficiency",
                "process automation",
                "workflow orchestration",
                "digital transformation",
                "AI-powered operations",
            ],
        },
        "scoring_weights": DEFAULT_SCORING_WEIGHTS,
    }


async def seed() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    data = build_icp_data()

    async with async_session() as session:
        result = await session.execute(
            select(ICPModel).where(ICPModel.name == data["name"])
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.description = data["description"]
            existing.criteria = data["criteria"]
            existing.scoring_weights = data["scoring_weights"]
            existing.is_active = True
            print(f"Updated existing ICP model: {existing.id}")
        else:
            model = ICPModel(
                name=data["name"],
                description=data["description"],
                criteria=data["criteria"],
                scoring_weights=data["scoring_weights"],
                is_active=True,
            )
            session.add(model)
            print("Created new ICP model.")

        await session.commit()
        print("Done — ICP seeded successfully.")


if __name__ == "__main__":
    asyncio.run(seed())
