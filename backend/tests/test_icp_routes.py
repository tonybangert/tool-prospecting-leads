"""Tests for ICP CRUD routes."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_icp_model(client: AsyncClient):
    resp = await client.post("/api/icp/", json={"name": "Mid-market SaaS"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Mid-market SaaS"
    assert data["version"] == "1.0"
    assert data["is_active"] is False
    assert "id" in data


@pytest.mark.asyncio
async def test_list_icp_models(client: AsyncClient):
    await client.post("/api/icp/", json={"name": "ICP A"})
    await client.post("/api/icp/", json={"name": "ICP B"})
    resp = await client.get("/api/icp/")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_list_filter_active(client: AsyncClient):
    resp = await client.get("/api/icp/", params={"is_active": "true"})
    assert resp.status_code == 200
    assert len(resp.json()) == 0


@pytest.mark.asyncio
async def test_get_icp_model(client: AsyncClient):
    create = await client.post("/api/icp/", json={"name": "Test"})
    model_id = create.json()["id"]

    resp = await client.get(f"/api/icp/{model_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Test"


@pytest.mark.asyncio
async def test_get_icp_model_not_found(client: AsyncClient):
    resp = await client.get("/api/icp/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_icp_model(client: AsyncClient):
    create = await client.post("/api/icp/", json={"name": "Original"})
    model_id = create.json()["id"]

    resp = await client.patch(f"/api/icp/{model_id}", json={"name": "Updated"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated"


@pytest.mark.asyncio
async def test_activate_icp_model(client: AsyncClient):
    r1 = await client.post("/api/icp/", json={"name": "A"})
    r2 = await client.post("/api/icp/", json={"name": "B"})
    id_a = r1.json()["id"]
    id_b = r2.json()["id"]

    # Activate A
    resp = await client.post(f"/api/icp/{id_a}/activate")
    assert resp.status_code == 200
    assert resp.json()["is_active"] is True

    # Activate B — A should deactivate
    resp = await client.post(f"/api/icp/{id_b}/activate")
    assert resp.json()["is_active"] is True

    get_a = await client.get(f"/api/icp/{id_a}")
    assert get_a.json()["is_active"] is False
