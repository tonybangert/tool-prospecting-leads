"""Map ICP criteria to Apollo contacts/search API filter parameters.

Apollo free-tier endpoint: POST /v1/contacts/search
Supported filters (verified):
  - q_person_title: string (title keyword search)
  - person_seniorities: list[str]
  - organization_num_employees_ranges: list[str] (bucket tokens)
  - organization_locations: list[str]
  - q_keywords: string (general keyword search — used for industry)
"""

# Apollo employee-range bucket tokens
_EMPLOYEE_BUCKETS = [
    ("1,10", 1, 10),
    ("11,20", 11, 20),
    ("21,50", 21, 50),
    ("51,100", 51, 100),
    ("101,200", 101, 200),
    ("201,500", 201, 500),
    ("501,1000", 501, 1000),
    ("1001,2000", 1001, 2000),
    ("2001,5000", 2001, 5000),
    ("5001,10000", 5001, 10000),
    ("10001,", 10001, float("inf")),
]


def map_icp_to_apollo_filters(criteria: dict) -> dict:
    """Convert an ICP criteria dict into Apollo contacts/search filter params.

    Args:
        criteria: ICP criteria with keys like industries, employee_range,
                  revenue_range, geographies, technologies, personas, keywords.

    Returns:
        Dict of Apollo API filter parameters.
    """
    filters: dict = {}

    # Industries → q_keywords (organization_industry_tag_ids not available on free tier)
    industries = criteria.get("industries", [])
    keywords = criteria.get("keywords", [])
    keyword_parts = list(industries) + list(keywords)
    if keyword_parts:
        filters["q_keywords"] = " ".join(keyword_parts)

    # Employee range → Apollo bucket tokens
    emp_range = criteria.get("employee_range")
    if emp_range:
        buckets = _employee_range_to_buckets(
            emp_range.get("min", 0),
            emp_range.get("max", float("inf")),
        )
        if buckets:
            filters["organization_num_employees_ranges"] = buckets

    # Geographies → organization_locations
    geos = criteria.get("geographies", [])
    if geos:
        filters["organization_locations"] = geos

    # Personas → person titles + seniorities
    personas = criteria.get("personas", [])
    if personas:
        titles = [p.get("title") for p in personas if p.get("title")]
        seniorities = [p.get("seniority") for p in personas if p.get("seniority")]
        if titles:
            filters["q_person_title"] = titles
        if seniorities:
            filters["person_seniorities"] = seniorities

    return filters


def _employee_range_to_buckets(min_emp: int, max_emp: float) -> list[str]:
    """Select Apollo bucket tokens that overlap with the ICP employee range."""
    selected = []
    for token, bucket_min, bucket_max in _EMPLOYEE_BUCKETS:
        if bucket_max >= min_emp and bucket_min <= max_emp:
            selected.append(token)
    return selected
