"""ICP fit scoring — compares an account against an ICP model's criteria."""

from typing import Any


def score_discovered_prospect(parsed_data: dict, icp_model: dict) -> dict[str, Any]:
    """Score a prospect discovered via Google CSE + Claude extraction.

    Uses the same sub-scoring logic as Apollo prospects but expects lower
    data confidence since most fields are inferred from LinkedIn snippets.
    """
    account = {
        "industry": parsed_data.get("industry", ""),
        "employee_count": parsed_data.get("employee_count"),
        "estimated_revenue": None,
        "technologies": [],
        "location": parsed_data.get("location", ""),
        "personas": [{"title": parsed_data.get("title", "")}] if parsed_data.get("title") else [],
    }

    score = calculate_icp_fit(account, icp_model)

    criteria = icp_model.get("criteria", {})
    breakdown = {
        "firmographic_fit": _score_firmographic(account, criteria),
        "tech_fit": 0.5,  # No tech data from LinkedIn snippets
        "persona_match": _score_persona(account, criteria),
        "timing_signals": _score_timing_signals(account, criteria),
        "data_confidence": 0.3,  # Low confidence — snippet-inferred data
    }

    return {"score": round(score, 4), "breakdown": breakdown}


def score_apollo_person(person: dict, icp_model: dict) -> dict[str, Any]:
    """Score an Apollo person/contact against an ICP model.

    Maps Apollo's person + organization fields into the account format
    expected by calculate_icp_fit, then returns score + sub-score breakdown.

    Args:
        person: Normalized Apollo person dict (with 'organization' sub-object).
        icp_model: ICP model dict with 'criteria' and 'scoring_weights'.

    Returns:
        {"score": float, "breakdown": dict} with overall fit and sub-scores.
    """
    org = person.get("organization") or {}

    # Build location from available parts
    location_parts = [
        org.get("city"),
        org.get("state"),
        org.get("country"),
    ]
    location = ", ".join(p for p in location_parts if p) or org.get("raw_address", "")

    account = {
        "industry": (
            org.get("industry")
            or person.get("organization_industry")
            or org.get("industry_tag_id")
            or ""
        ),
        "employee_count": (
            org.get("estimated_num_employees")
            or org.get("employee_count")
        ),
        "estimated_revenue": org.get("annual_revenue"),
        "technologies": org.get("technologies", []) or [],
        "location": location,
        "personas": [{"title": person.get("title", "")}] if person.get("title") else [],
    }

    score = calculate_icp_fit(account, icp_model)

    # Compute sub-scores for the breakdown
    criteria = icp_model.get("criteria", {})
    breakdown = {
        "firmographic_fit": _score_firmographic(account, criteria),
        "tech_fit": _score_tech(account, criteria),
        "persona_match": _score_persona(account, criteria),
        "timing_signals": _score_timing_signals(account, criteria),
        "data_confidence": _score_data_confidence(account),
    }

    return {"score": round(score, 4), "breakdown": breakdown}


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
        "timing_signals": _score_timing_signals(account, criteria),
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

    # Industry: case-insensitive match with substring fallback
    icp_industries = {i.lower() for i in criteria.get("industries", [])}
    if icp_industries:
        acct_industry = (account.get("industry") or "").lower()
        if acct_industry in icp_industries:
            parts.append(1.0)
        elif any(icp in acct_industry or acct_industry in icp for icp in icp_industries):
            parts.append(0.8)  # Partial match (e.g. "technology" in "information technology")
        else:
            parts.append(0.0)

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


def _normalize_title(title: str) -> set[str]:
    """Expand a title into a set of matchable variants.

    Handles C-suite abbreviations ↔ full forms and common synonyms so that
    "CEO" matches "Chief Executive Officer" and vice versa.
    """
    t = title.lower().strip()
    variants = {t}

    # C-suite abbreviation ↔ full form mapping
    _ALIASES = {
        "ceo": {"chief executive officer"},
        "coo": {"chief operating officer"},
        "cro": {"chief revenue officer"},
        "cfo": {"chief financial officer"},
        "cto": {"chief technology officer"},
        "cmo": {"chief marketing officer"},
        "cio": {"chief information officer"},
        "cpo": {"chief product officer"},
        "vp of operations": {"vice president of operations", "vp operations"},
        "vp of sales": {"vice president of sales", "vp sales"},
    }

    # If title IS an abbreviation, add full forms
    if t in _ALIASES:
        variants.update(_ALIASES[t])

    # If title contains a full form, add abbreviation
    for abbr, full_forms in _ALIASES.items():
        for full in full_forms:
            if full in t:
                variants.add(abbr)

    return variants


def _score_persona(account: dict, criteria: dict) -> float:
    """Check if any account personas match ICP persona titles.

    Uses precision (fraction of prospect's titles that match ICP) rather than
    recall. A single prospect is one person — if their title matches ANY ICP
    persona, that's a strong signal (1.0). Recall would cap at 1/N for N
    target personas, punishing good matches.

    Normalizes titles via alias expansion (CEO ↔ Chief Executive Officer)
    and falls back to fuzzy matching for remaining variations.
    """
    icp_personas = criteria.get("personas", [])
    if not icp_personas:
        return 0.5  # No persona criteria — neutral

    # Expand ICP titles into all matchable variants
    icp_variants: set[str] = set()
    for p in icp_personas:
        icp_variants.update(_normalize_title(p.get("title", "")))

    acct_personas = account.get("personas", [])
    if not acct_personas:
        return 0.0

    acct_variants: set[str] = set()
    for p in acct_personas:
        title = p if isinstance(p, str) else p.get("title", "")
        acct_variants.update(_normalize_title(title))

    if not acct_variants:
        return 0.0

    # Exact match after normalization
    if icp_variants & acct_variants:
        return 1.0

    # Fuzzy: substring and keyword overlap
    for acct_title in acct_variants:
        for icp_title in icp_variants:
            if icp_title in acct_title or acct_title in icp_title:
                return 0.8
            icp_words = {w for w in icp_title.split() if len(w) > 2}
            acct_words = {w for w in acct_title.split() if len(w) > 2}
            if icp_words and acct_words:
                word_overlap = len(icp_words & acct_words) / len(icp_words)
                if word_overlap >= 0.5:
                    return 0.6

    return 0.0


def _score_timing_signals(account: dict, criteria: dict) -> float:
    """Score presence of buying-trigger keywords in prospect data.

    Scans the account's text fields (industry, location, persona titles, and
    any extra discovery_data) for matches against the ICP's buying_triggers.
    Returns 0.5 (neutral) when no buying triggers are defined.
    """
    triggers = criteria.get("buying_triggers", [])
    if not triggers:
        return 0.5  # No triggers defined — neutral, backwards compatible

    trigger_terms = [t.lower() for t in triggers]

    # Collect searchable text from the account
    text_parts = [
        account.get("industry", ""),
        account.get("location", ""),
    ]
    for p in account.get("personas", []):
        title = p if isinstance(p, str) else p.get("title", "")
        text_parts.append(title)
        if isinstance(p, dict):
            text_parts.append(p.get("context", ""))

    # Include discovery_data if present (prospect researcher stores extra info here)
    discovery = account.get("discovery_data")
    if isinstance(discovery, dict):
        text_parts.extend(str(v) for v in discovery.values())
    elif isinstance(discovery, str):
        text_parts.append(discovery)

    searchable = " ".join(text_parts).lower()
    if not searchable.strip():
        return 0.5  # No data to search — neutral

    matched = sum(1 for term in trigger_terms if term in searchable)
    return min(matched / len(trigger_terms), 1.0)


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
