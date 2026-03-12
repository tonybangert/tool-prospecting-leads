"""Tests for ICP criteria → Apollo filter mapping."""

from app.services.icp_filter_mapper import map_icp_to_apollo_filters


def test_full_criteria():
    criteria = {
        "industries": ["SaaS", "Technology"],
        "employee_range": {"min": 50, "max": 500},
        "geographies": ["United States"],
        "personas": [
            {"title": "VP of Sales", "seniority": "VP"},
            {"title": "CTO", "seniority": "C-Suite"},
        ],
        "keywords": ["B2B"],
    }
    filters = map_icp_to_apollo_filters(criteria)

    # Industries + keywords merged into q_keywords
    assert "q_keywords" in filters
    assert "SaaS" in filters["q_keywords"]
    assert "B2B" in filters["q_keywords"]

    # Employee buckets
    assert "organization_num_employees_ranges" in filters
    buckets = filters["organization_num_employees_ranges"]
    assert "51,100" in buckets
    assert "201,500" in buckets

    # Geographies
    assert filters["organization_locations"] == ["United States"]

    # Personas
    assert filters["q_person_title"] == ["VP of Sales", "CTO"]
    assert filters["person_seniorities"] == ["VP", "C-Suite"]


def test_empty_criteria():
    filters = map_icp_to_apollo_filters({})
    assert filters == {}


def test_industries_only():
    filters = map_icp_to_apollo_filters({"industries": ["FinTech"]})
    assert filters["q_keywords"] == "FinTech"
    assert "organization_num_employees_ranges" not in filters


def test_employee_range_single_bucket():
    filters = map_icp_to_apollo_filters({"employee_range": {"min": 1, "max": 10}})
    assert filters["organization_num_employees_ranges"] == ["1,10"]
