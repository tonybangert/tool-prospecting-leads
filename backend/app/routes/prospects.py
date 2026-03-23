"""Prospect pipeline routes: Discover → Select → Enrich."""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.icp import ICPModel
from app.models.prospect import Prospect
from app.schemas.prospect import (
    DiscoverRequest,
    EnrichRequest,
    ProspectListResponse,
    ProspectResponse,
    SelectProspectsRequest,
)
from app.services.apollo import ApolloService
from app.services.prospect_researcher import ProspectResearcher
from app.services.scoring import score_apollo_person, score_discovered_prospect

router = APIRouter(prefix="/api/prospects", tags=["prospects"])


@router.post("/discover/{model_id}", response_model=ProspectListResponse)
async def discover_prospects(
    model_id: uuid.UUID,
    body: DiscoverRequest | None = None,
    session: AsyncSession = Depends(get_session),
):
    """Phase 1: Use Claude web_search to discover prospects from LinkedIn."""
    if body is None:
        body = DiscoverRequest()

    icp_model = await session.get(ICPModel, model_id)
    if not icp_model:
        raise HTTPException(status_code=404, detail="ICP model not found")

    icp_dict = {
        "criteria": icp_model.criteria,
        "scoring_weights": icp_model.scoring_weights,
    }

    # Claude searches the web and extracts structured prospects in one call
    researcher = ProspectResearcher()
    try:
        parsed_prospects = await researcher.discover_prospects(icp_model.criteria)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Discovery error: {exc}")

    if not parsed_prospects:
        return await _list_prospects(session, model_id, status_filter="discovered")

    # Score and persist — drop prospects scoring below threshold
    MIN_DISCOVERY_SCORE = 0.25
    for parsed in parsed_prospects:
        scored = score_discovered_prospect(parsed, icp_dict)

        if scored["score"] < MIN_DISCOVERY_SCORE:
            continue

        linkedin_url = parsed.get("linkedin_url")

        # Dedup by linkedin_url + model
        if linkedin_url:
            existing = await session.execute(
                select(Prospect).where(
                    Prospect.icp_model_id == model_id,
                    Prospect.linkedin_url == linkedin_url,
                )
            )
            if existing.scalar_one_or_none():
                continue

        prospect = Prospect(
            icp_model_id=model_id,
            first_name=parsed.get("first_name"),
            last_name=parsed.get("last_name"),
            title=parsed.get("title"),
            seniority=parsed.get("seniority"),
            linkedin_url=linkedin_url,
            company_name=parsed.get("company_name"),
            industry=parsed.get("industry"),
            company_location=parsed.get("location"),
            icp_fit_score=scored["score"],
            score_breakdown=scored["breakdown"],
            source="web_search",
            discovery_data={
                "icp_fit_summary": parsed.get("icp_fit_summary"),
            },
            status="discovered",
        )
        session.add(prospect)

    await session.commit()
    return await _list_prospects(session, model_id, status_filter="discovered")


@router.post("/select/{model_id}", response_model=ProspectListResponse)
async def select_prospects(
    model_id: uuid.UUID,
    body: SelectProspectsRequest,
    session: AsyncSession = Depends(get_session),
):
    """Phase 2: Mark discovered prospects as selected for enrichment."""
    icp_model = await session.get(ICPModel, model_id)
    if not icp_model:
        raise HTTPException(status_code=404, detail="ICP model not found")

    stmt = select(Prospect).where(
        Prospect.icp_model_id == model_id,
        Prospect.id.in_(body.prospect_ids),
        Prospect.status == "discovered",
    )
    result = await session.execute(stmt)
    prospects = result.scalars().all()

    if not prospects:
        raise HTTPException(status_code=404, detail="No matching discovered prospects found")

    for p in prospects:
        p.status = "selected"

    await session.commit()
    return await _list_prospects(session, model_id, status_filter="selected")


@router.post("/enrich/{model_id}", response_model=ProspectListResponse)
async def enrich_prospects(
    model_id: uuid.UUID,
    body: EnrichRequest,
    session: AsyncSession = Depends(get_session),
):
    """Phase 3: Enrich selected prospects via Apollo API."""
    icp_model = await session.get(ICPModel, model_id)
    if not icp_model:
        raise HTTPException(status_code=404, detail="ICP model not found")

    icp_dict = {
        "criteria": icp_model.criteria,
        "scoring_weights": icp_model.scoring_weights,
    }

    stmt = select(Prospect).where(
        Prospect.icp_model_id == model_id,
        Prospect.id.in_(body.prospect_ids),
        Prospect.status.in_(["selected", "enriched"]),
    )
    result = await session.execute(stmt)
    prospects = result.scalars().all()

    if not prospects:
        raise HTTPException(status_code=404, detail="No matching prospects found for enrichment")

    apollo = ApolloService()
    try:
        for prospect in prospects:
            person = None

            # Try Apollo match by LinkedIn URL first
            if prospect.linkedin_url:
                try:
                    person = await apollo.match_by_linkedin(prospect.linkedin_url)
                except Exception:
                    pass

            # Fallback: search by name + company
            if not person and prospect.first_name and prospect.company_name:
                try:
                    name = f"{prospect.first_name} {prospect.last_name or ''}".strip()
                    person = await apollo.search_by_name_and_company(
                        name, prospect.company_name
                    )
                except Exception:
                    pass

            if person:
                org = person.get("organization") or {}
                loc_parts = [org.get("city"), org.get("state"), org.get("country")]
                location = ", ".join(p for p in loc_parts if p) or ""

                scored = score_apollo_person(person, icp_dict)

                # Extract best phone number from Apollo's phone_numbers array
                phone_numbers = person.get("phone_numbers") or []
                best_phone = None
                if phone_numbers:
                    # Prefer mobile, then direct, then any
                    for ptype in ("mobile", "direct", None):
                        for pn in phone_numbers:
                            if ptype is None or pn.get("type") == ptype:
                                best_phone = pn.get("sanitized_number") or pn.get("raw_number")
                                break
                        if best_phone:
                            break

                prospect.apollo_person_id = person.get("id")
                prospect.email = person.get("email")
                prospect.phone = best_phone
                prospect.title = person.get("title") or prospect.title
                prospect.seniority = person.get("seniority") or prospect.seniority
                prospect.linkedin_url = person.get("linkedin_url") or prospect.linkedin_url
                prospect.company_name = org.get("name") or prospect.company_name
                prospect.company_domain = org.get("primary_domain") or org.get("website_url")
                prospect.industry = org.get("industry") or prospect.industry
                prospect.employee_count = org.get("estimated_num_employees") or org.get("employee_count")
                prospect.company_location = location or prospect.company_location
                prospect.icp_fit_score = scored["score"]
                prospect.score_breakdown = scored["breakdown"]
                prospect.apollo_data = person

            prospect.status = "enriched"
            prospect.enriched_at = datetime.now(timezone.utc)
    finally:
        await apollo.close()

    await session.commit()
    return await _list_prospects(session, model_id, status_filter="enriched")


@router.get("/{model_id}", response_model=ProspectListResponse)
async def list_prospects(
    model_id: uuid.UUID,
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    status: str | None = Query(None),
    session: AsyncSession = Depends(get_session),
):
    """List stored prospects for an ICP model, with optional status filter."""
    return await _list_prospects(session, model_id, page, per_page, status_filter=status)


async def _list_prospects(
    session: AsyncSession,
    model_id: uuid.UUID,
    page: int = 1,
    per_page: int = 25,
    status_filter: str | None = None,
) -> ProspectListResponse:
    """Shared helper to list prospects with pagination and optional status filter."""
    base_where = [Prospect.icp_model_id == model_id]
    if status_filter:
        base_where.append(Prospect.status == status_filter)

    count_stmt = select(func.count()).select_from(Prospect).where(*base_where)
    total = (await session.execute(count_stmt)).scalar() or 0

    stmt = (
        select(Prospect)
        .where(*base_where)
        .order_by(Prospect.icp_fit_score.desc().nulls_last())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    result = await session.execute(stmt)
    items = result.scalars().all()

    return ProspectListResponse(
        items=[ProspectResponse.model_validate(p) for p in items],
        total=total,
    )
