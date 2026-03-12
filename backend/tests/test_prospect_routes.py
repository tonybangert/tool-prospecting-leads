"""Tests for prospect search and list routes."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


MOCK_APOLLO_RESPONSE = {
    "contacts": [
        {
            "id": "apollo_001",
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane@example.com",
            "title": "VP of Sales",
            "seniority": "VP",
            "linkedin_url": "https://linkedin.com/in/janesmith",
            "organization_name": "Acme Corp",
            "organization_industry": "SaaS",
            "account": {
                "name": "Acme Corp",
                "primary_domain": "acme.com",
                "industry": "SaaS",
                "estimated_num_employees": 200,
                "city": "San Francisco",
                "state": "California",
                "country": "United States",
            },
        },
        {
            "id": "apollo_002",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "title": "Head of Revenue Operations",
            "seniority": "Director",
            "linkedin_url": None,
            "organization_name": "Beta Inc",
            "account": {
                "name": "Beta Inc",
                "primary_domain": "beta.io",
                "estimated_num_employees": 50,
                "city": "Austin",
                "state": "Texas",
                "country": "United States",
            },
        },
    ],
    "pagination": {"page": 1, "per_page": 25, "total_entries": 2},
}


@pytest.fixture
def mock_apollo():
    """Patch ApolloService.search_people to return mock data."""
    with patch("app.routes.prospects.ApolloService") as MockCls:
        instance = MockCls.return_value
        instance.search_people = AsyncMock(return_value={
            "people": [
                {**c, "organization": c.pop("account", {})}
                for c in [dict(ct) for ct in MOCK_APOLLO_RESPONSE["contacts"]]
            ],
            "pagination": MOCK_APOLLO_RESPONSE["pagination"],
        })
        instance.close = AsyncMock()
        yield instance


async def _create_icp(client: AsyncClient) -> str:
    """Helper to create an ICP model and return its ID."""
    resp = await client.post("/api/icp/", json={
        "name": "Test ICP",
        "criteria": {
            "industries": ["SaaS"],
            "employee_range": {"min": 50, "max": 500},
            "geographies": ["United States"],
            "personas": [{"title": "VP of Sales", "seniority": "VP"}],
        },
        "scoring_weights": {
            "firmographic_fit": 0.30,
            "tech_fit": 0.20,
            "persona_match": 0.20,
            "timing_signals": 0.15,
            "data_confidence": 0.15,
        },
    })
    assert resp.status_code == 201
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_search_prospects(client: AsyncClient, mock_apollo):
    model_id = await _create_icp(client)

    resp = await client.post(f"/api/prospects/search/{model_id}", json={"page": 1, "per_page": 25})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert data["items"][0]["icp_fit_score"] is not None


@pytest.mark.asyncio
async def test_search_deduplicates(client: AsyncClient, mock_apollo):
    model_id = await _create_icp(client)

    # Search twice — second search should skip already stored prospects
    await client.post(f"/api/prospects/search/{model_id}", json={})
    resp = await client.post(f"/api/prospects/search/{model_id}", json={})
    data = resp.json()
    assert data["total"] == 2  # same 2, not 4


@pytest.mark.asyncio
async def test_list_prospects(client: AsyncClient, mock_apollo):
    model_id = await _create_icp(client)

    # Before search — empty
    resp = await client.get(f"/api/prospects/{model_id}")
    assert resp.status_code == 200
    assert resp.json()["total"] == 0

    # After search
    await client.post(f"/api/prospects/search/{model_id}", json={})
    resp = await client.get(f"/api/prospects/{model_id}")
    data = resp.json()
    assert data["total"] == 2
    # Should be sorted by score descending
    scores = [p["icp_fit_score"] for p in data["items"]]
    assert scores == sorted(scores, reverse=True)


@pytest.mark.asyncio
async def test_search_not_found_icp(client: AsyncClient):
    resp = await client.post(
        "/api/prospects/search/00000000-0000-0000-0000-000000000000",
        json={},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_prospect_has_score_breakdown(client: AsyncClient, mock_apollo):
    model_id = await _create_icp(client)
    await client.post(f"/api/prospects/search/{model_id}", json={})

    resp = await client.get(f"/api/prospects/{model_id}")
    prospect = resp.json()["items"][0]
    assert "score_breakdown" in prospect
    assert "firmographic_fit" in (prospect["score_breakdown"] or {})
