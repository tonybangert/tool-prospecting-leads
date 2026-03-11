"""Tests for the Subscription Ecosystem Dashboard API endpoints."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_kpis():
    resp = client.get("/api/dashboard/kpis")
    assert resp.status_code == 200
    data = resp.json()
    assert "mrr" in data
    assert "total_subscribers" in data
    assert "active_rate" in data
    assert "arpu" in data
    assert "avg_engagement" in data
    assert "churn_rate" in data
    assert data["total_subscribers"] == 50


def test_subscribers():
    resp = client.get("/api/subscribers")
    assert resp.status_code == 200
    data = resp.json()
    assert "status_distribution" in data
    assert "tier_distribution" in data
    assert "snapshot" in data
    assert len(data["snapshot"]) <= 10
    assert sum(data["status_distribution"].values()) == 50


def test_churn():
    resp = client.get("/api/churn")
    assert resp.status_code == 200
    data = resp.json()
    assert "scatter_data" in data
    assert "risk_distribution" in data
    assert "high_risk_subscribers" in data
    assert len(data["scatter_data"]) == 50
    for point in data["scatter_data"]:
        assert "engagement_score" in point
        assert "risk_score" in point


def test_segments():
    resp = client.get("/api/segments")
    assert resp.status_code == 200
    data = resp.json()
    assert "axes" in data
    assert "segments" in data
    assert len(data["axes"]) == 5
    assert len(data["segments"]) == 6
    for seg in data["segments"]:
        assert "name" in seg
        assert "radar_values" in seg
        assert len(seg["radar_values"]) == 5


def test_recommendations():
    resp = client.get("/api/recommendations")
    assert resp.status_code == 200
    data = resp.json()
    assert "recommendations" in data
    assert "total_projected_monthly_impact" in data
    assert len(data["recommendations"]) == 6
    assert data["total_projected_monthly_impact"] > 0


def test_revenue_forecast():
    resp = client.get("/api/revenue-forecast")
    assert resp.status_code == 200
    data = resp.json()
    assert "historical" in data
    assert "projected_baseline" in data
    assert "projected_ai_enhanced" in data
    assert "current_mrr" in data
    assert "ai_uplift_pct" in data
    assert len(data["historical"]) == 15
    assert len(data["projected_baseline"]) == 12


def test_retention_actions():
    resp = client.get("/api/retention-actions")
    assert resp.status_code == 200
    data = resp.json()
    assert "actions" in data
    assert "summary" in data
    assert len(data["actions"]) == 15
    assert data["summary"]["total"] == 15
    assert data["summary"]["completed"] + data["summary"]["in_progress"] + data["summary"]["pending"] == 15
