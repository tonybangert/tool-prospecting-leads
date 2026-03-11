"""ICP fit scoring — compares an account against an ICP model's criteria."""


def calculate_icp_fit(account: dict, icp_model: dict) -> float:
    """Score how well an account matches an ICP model (0.0 to 1.0).

    Args:
        account: Account/organization data from Apollo or similar source.
            Expected keys: industry, employee_count, estimated_revenue,
            technologies, location, personas.
        icp_model: ICP model dict with 'criteria' and 'scoring_weights' keys.
            criteria contains: industries, employee_range, revenue_range,
            technologies, geographies, personas.
            scoring_weights contains: firmographic_fit, tech_fit,
            persona_match, timing_signals, data_confidence.

    Returns:
        Float between 0.0 and 1.0 representing overall fit.
    """
    criteria = icp_model.get("criteria", {})
    weights = icp_model.get("scoring_weights", {})

    if not criteria or not weights:
        return 0.0

    sub_scores = {
        "firmographic_fit": _score_firmographic(account, criteria),
        "tech_fit": _score_tech(account, criteria),
        "persona_match": _score_persona(account, criteria),
        "timing_signals": 0.5,  # Phase 2 placeholder
        "data_confidence": _score_data_confidence(account),
    }

    total = sum(
        weights.get(category, 0.0) * score
        for category, score in sub_scores.items()
    )

    return min(max(total, 0.0), 1.0)


def _score_firmographic(account: dict, criteria: dict) -> float:
    """Industry match, employee range, revenue range, geography — averaged."""
    parts: list[float] = []

    # Industry: exact case-insensitive match against ICP list
    icp_industries = {i.lower() for i in criteria.get("industries", [])}
    if icp_industries:
        acct_industry = (account.get("industry") or "").lower()
        parts.append(1.0 if acct_industry in icp_industries else 0.0)

    # Employee count: gradient scoring — full marks inside range, linear
    # falloff up to 2x outside, then zero.
    emp_range = criteria.get("employee_range")
    emp_count = account.get("employee_count")
    if emp_range and emp_count is not None:
        parts.append(_range_score(emp_count, emp_range.get("min", 0), emp_range.get("max", 0)))

    # Revenue: same gradient approach
    rev_range = criteria.get("revenue_range")
    revenue = account.get("estimated_revenue")
    if rev_range and revenue is not None:
        parts.append(_range_score(revenue, rev_range.get("min", 0), rev_range.get("max", 0)))

    # Geography: account location in ICP geography list
    icp_geos = {g.lower() for g in criteria.get("geographies", [])}
    if icp_geos:
        acct_location = (account.get("location") or "").lower()
        parts.append(1.0 if any(geo in acct_location for geo in icp_geos) else 0.0)

    return sum(parts) / len(parts) if parts else 0.0


def _range_score(value: float, range_min: float, range_max: float) -> float:
    """Score a numeric value against a target range.

    1.0 if within range, linear falloff to 0.0 at 2x the range width outside.
    """
    if range_max <= range_min:
        return 0.0
    if range_min <= value <= range_max:
        return 1.0
    width = range_max - range_min
    if value < range_min:
        distance = range_min - value
    else:
        distance = value - range_max
    return max(0.0, 1.0 - distance / width)


def _score_tech(account: dict, criteria: dict) -> float:
    """Technology overlap: |intersection| / |icp_set| (recall-oriented).

    Using recall (what fraction of desired techs does the account have)
    rather than Jaccard avoids penalizing accounts that use many extra techs.
    """
    icp_techs = {t.lower() for t in criteria.get("technologies", [])}
    if not icp_techs:
        return 0.5  # No tech criteria — neutral
    acct_techs = {t.lower() for t in account.get("technologies", [])}
    if not acct_techs:
        return 0.0
    overlap = len(icp_techs & acct_techs)
    return overlap / len(icp_techs)


def _score_persona(account: dict, criteria: dict) -> float:
    """Check if any account personas match ICP persona titles."""
    icp_personas = criteria.get("personas", [])
    if not icp_personas:
        return 0.5  # No persona criteria — neutral
    icp_titles = {p.get("title", "").lower() for p in icp_personas}
    acct_personas = account.get("personas", [])
    if not acct_personas:
        return 0.0
    acct_titles = set()
    for p in acct_personas:
        title = p if isinstance(p, str) else p.get("title", "")
        acct_titles.add(title.lower())

    if not acct_titles:
        return 0.0
    overlap = len(icp_titles & acct_titles)
    return min(overlap / len(icp_titles), 1.0)


def _score_data_confidence(account: dict) -> float:
    """Penalize sparse account data. Score = fraction of key fields present."""
    expected_fields = [
        "industry", "employee_count", "estimated_revenue",
        "technologies", "location", "personas",
    ]
    present = sum(1 for f in expected_fields if account.get(f))
    return present / len(expected_fields)


def _employee_count_to_size_label(count: int) -> str:
    """Convert an employee count into a named size bucket."""
    if count < 10:
        return "micro"
    if count < 50:
        return "small"
    if count < 200:
        return "mid-market"
    if count < 1000:
        return "mid-enterprise"
    if count < 5000:
        return "enterprise"
    return "large-enterprise"
