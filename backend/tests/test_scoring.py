"""Tests for ICP fit scoring."""

from app.services.scoring import _employee_count_to_size_label, calculate_icp_fit


SAMPLE_ICP = {
    "criteria": {
        "industries": ["SaaS", "Technology"],
        "employee_range": {"min": 50, "max": 500},
        "revenue_range": {"min": 5_000_000, "max": 50_000_000},
        "geographies": ["United States"],
        "technologies": ["Salesforce", "HubSpot", "Slack"],
        "personas": [
            {"title": "VP of Sales", "seniority": "VP"},
            {"title": "Head of Revenue Operations", "seniority": "Director"},
        ],
    },
    "scoring_weights": {
        "firmographic_fit": 0.30,
        "tech_fit": 0.20,
        "persona_match": 0.20,
        "timing_signals": 0.15,
        "data_confidence": 0.15,
    },
}


def test_employee_size_labels():
    assert _employee_count_to_size_label(5) == "micro"
    assert _employee_count_to_size_label(25) == "small"
    assert _employee_count_to_size_label(100) == "mid-market"
    assert _employee_count_to_size_label(500) == "mid-enterprise"
    assert _employee_count_to_size_label(2000) == "enterprise"
    assert _employee_count_to_size_label(10000) == "large-enterprise"


def test_perfect_match():
    account = {
        "industry": "SaaS",
        "employee_count": 200,
        "estimated_revenue": 20_000_000,
        "location": "United States",
        "technologies": ["Salesforce", "HubSpot", "Slack", "Jira"],
        "personas": [
            {"title": "VP of Sales"},
            {"title": "Head of Revenue Operations"},
        ],
    }
    score = calculate_icp_fit(account, SAMPLE_ICP)
    assert score > 0.85, f"Perfect match should score high, got {score}"


def test_no_match():
    account = {
        "industry": "Agriculture",
        "employee_count": 5,
        "estimated_revenue": 100_000,
        "location": "Antarctica",
        "technologies": ["Excel"],
        "personas": [{"title": "Farm Manager"}],
    }
    score = calculate_icp_fit(account, SAMPLE_ICP)
    # timing_signals (0.5) + data_confidence (all fields present) create a
    # floor around 0.22 even with zero match on actual criteria
    assert score < 0.4, f"No match should score low, got {score}"


def test_partial_match():
    account = {
        "industry": "SaaS",
        "employee_count": 800,  # outside range but close
        "estimated_revenue": 20_000_000,
        "location": "United States",
        "technologies": ["Salesforce"],  # 1 of 3
        "personas": [{"title": "VP of Sales"}],  # 1 of 2
    }
    score = calculate_icp_fit(account, SAMPLE_ICP)
    assert 0.3 < score < 0.85, f"Partial match should be mid-range, got {score}"


def test_empty_inputs():
    assert calculate_icp_fit({}, {}) == 0.0
    assert calculate_icp_fit({}, SAMPLE_ICP) < 0.2


def test_returns_bounded_float():
    score = calculate_icp_fit({"industry": "SaaS"}, SAMPLE_ICP)
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0
