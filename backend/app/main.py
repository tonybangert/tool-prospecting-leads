import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure the backend directory is on sys.path so `agents` package is importable
_backend_dir = str(Path(__file__).resolve().parent.parent)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from app.routes.icp import router as icp_router
from app.routes.prospects import router as prospects_router
from app.sample_data import (
    SUBSCRIBERS,
    BEHAVIORAL_DATA,
    CHURN_PREDICTIONS,
    SEGMENTS,
    SEGMENT_AXES,
    RECOMMENDATIONS,
    RETENTION_ACTIONS,
)
from app.data_generators import (
    compute_kpi_summary,
    compute_status_distribution,
    compute_tier_distribution,
    compute_engagement_vs_churn,
    compute_monthly_metrics,
)

app = FastAPI(
    title="AI-Powered Subscription Ecosystem Dashboard",
    description="Demo dashboard for PerformanceLabs — The Motley Fool subscriber intelligence",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(icp_router)
app.include_router(prospects_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/api/dashboard/kpis")
async def get_kpis():
    """Top-line KPI metrics: MRR, subscribers, active rate, ARPU, engagement, churn."""
    return compute_kpi_summary()


@app.get("/api/subscribers")
async def get_subscribers():
    """Subscriber profiles with status and tier distributions for doughnut charts."""
    snapshot = []
    for s in SUBSCRIBERS[:10]:
        b = BEHAVIORAL_DATA.get(s["id"], {})
        snapshot.append({
            "id": s["id"],
            "name": s["name"],
            "plan_tier": s["plan_tier"],
            "status": s["status"],
            "tenure_months": s["tenure_months"],
            "monthly_rate": s["monthly_rate"],
            "engagement_score": b.get("engagement_score", 0),
        })
    return {
        "status_distribution": compute_status_distribution(),
        "tier_distribution": compute_tier_distribution(),
        "snapshot": snapshot,
    }


@app.get("/api/churn")
async def get_churn():
    """Churn predictions: scatter data, risk distribution, high-risk subscriber details."""
    scatter_data = compute_engagement_vs_churn()

    risk_counts = {"low": 0, "medium": 0, "high": 0}
    for pred in CHURN_PREDICTIONS.values():
        risk_counts[pred["risk_level"]] = risk_counts.get(pred["risk_level"], 0) + 1

    high_risk = []
    for s in SUBSCRIBERS:
        pred = CHURN_PREDICTIONS.get(s["id"])
        if pred and pred["risk_level"] == "high":
            b = BEHAVIORAL_DATA.get(s["id"], {})
            high_risk.append({
                "id": s["id"],
                "name": s["name"],
                "plan_tier": s["plan_tier"],
                "status": s["status"],
                "risk_score": pred["risk_score"],
                "contributing_factors": pred["contributing_factors"],
                "engagement_score": b.get("engagement_score", 0),
                "monthly_rate": s["monthly_rate"],
            })
    high_risk.sort(key=lambda x: x["risk_score"], reverse=True)

    return {
        "scatter_data": scatter_data,
        "risk_distribution": risk_counts,
        "high_risk_subscribers": high_risk[:8],
    }


@app.get("/api/segments")
async def get_segments():
    """AI-discovered behavioral segments with radar chart data."""
    return {
        "axes": SEGMENT_AXES,
        "segments": SEGMENTS,
    }


@app.get("/api/recommendations")
async def get_recommendations():
    """Upsell and retention recommendations per segment with revenue impact."""
    total_impact = sum(
        action["projected_monthly_impact"]
        for rec in RECOMMENDATIONS
        for action in rec["actions"]
    )
    return {
        "recommendations": RECOMMENDATIONS,
        "total_projected_monthly_impact": total_impact,
    }


@app.get("/api/revenue-forecast")
async def get_revenue_forecast():
    """Historical + projected MRR: baseline vs AI-enhanced."""
    metrics = compute_monthly_metrics()
    baseline_final = metrics["projected_baseline"][-1]["mrr"]
    ai_final = metrics["projected_ai_enhanced"][-1]["mrr"]
    current = metrics["historical"][-1]["mrr"]
    return {
        **metrics,
        "current_mrr": current,
        "baseline_projected_mrr": baseline_final,
        "ai_projected_mrr": ai_final,
        "ai_uplift_pct": round((ai_final - baseline_final) / baseline_final * 100, 1),
    }


@app.get("/api/retention-actions")
async def get_retention_actions():
    """AI agent action log — recent automated retention activities."""
    completed = len([a for a in RETENTION_ACTIONS if a["status"] == "completed"])
    in_progress = len([a for a in RETENTION_ACTIONS if a["status"] == "in_progress"])
    pending = len([a for a in RETENTION_ACTIONS if a["status"] == "pending"])
    return {
        "actions": RETENTION_ACTIONS,
        "summary": {
            "total": len(RETENTION_ACTIONS),
            "completed": completed,
            "in_progress": in_progress,
            "pending": pending,
        },
    }
