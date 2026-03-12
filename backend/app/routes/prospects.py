"""Prospect search and list routes."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.icp import ICPModel
from app.models.prospect import Prospect
from app.schemas.prospect import ProspectListResponse, ProspectResponse, SearchRequest
from app.services.apollo import ApolloService
from app.services.icp_filter_mapper import map_icp_to_apollo_filters
from app.services.scoring import score_apollo_person

router = APIRouter(prefix="/api/prospects", tags=["prospects"])


@router.post("/search/{model_id}", response_model=ProspectListResponse)
async def search_prospects(
    model_id: uuid.UUID,
    body: SearchRequest | None = None,
    session: AsyncSession = Depends(get_session),
):
    """Search Apollo for prospects matching an ICP model, score and persist them."""
    if body is None:
        body = SearchRequest()

    # Fetch the ICP model
    icp_model = await session.get(ICPModel, model_id)
    if not icp_model:
        raise HTTPException(status_code=404, detail="ICP model not found")

    # Map ICP criteria to Apollo filters
    filters = map_icp_to_apollo_filters(icp_model.criteria)
    filters["page"] = body.page
    filters["per_page"] = body.per_page

    # Search Apollo
    apollo = ApolloService()
    try:
        results = await apollo.search_people(filters)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Apollo API error: {exc}")
    finally:
        await apollo.close()

    icp_dict = {
        "criteria": icp_model.criteria,
        "scoring_weights": icp_model.scoring_weights,
    }

    # Score and persist each person
    prospects: list[Prospect] = []
    for person in results.get("people", []):
        apollo_id = person.get("id")

        # Dedup: skip if we already have this person for this ICP
        if apollo_id:
            existing = await session.execute(
                select(Prospect).where(
                    Prospect.icp_model_id == model_id,
                    Prospect.apollo_person_id == apollo_id,
                )
            )
            if existing.scalar_one_or_none():
                continue

        scored = score_apollo_person(person, icp_dict)
        org = person.get("organization") or {}

        # Build location from org parts
        loc_parts = [org.get("city"), org.get("state"), org.get("country")]
        location = ", ".join(p for p in loc_parts if p) or ""

        prospect = Prospect(
            icp_model_id=model_id,
            apollo_person_id=apollo_id,
            first_name=person.get("first_name"),
            last_name=person.get("last_name"),
            email=person.get("email"),
            title=person.get("title"),
            seniority=person.get("seniority"),
            linkedin_url=person.get("linkedin_url"),
            company_name=org.get("name") or person.get("organization_name"),
            company_domain=org.get("primary_domain") or org.get("website_url"),
            industry=org.get("industry") or person.get("organization_industry"),
            employee_count=org.get("estimated_num_employees") or org.get("employee_count"),
            company_location=location,
            icp_fit_score=scored["score"],
            score_breakdown=scored["breakdown"],
            apollo_data=person,
            status="scored",
        )
        session.add(prospect)
        prospects.append(prospect)

    await session.commit()

    # Refresh to get IDs / defaults
    for p in prospects:
        await session.refresh(p)

    # Return all prospects for this model (sorted by score desc)
    return await _list_prospects(session, model_id)


@router.get("/{model_id}", response_model=ProspectListResponse)
async def list_prospects(
    model_id: uuid.UUID,
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    """List stored prospects for an ICP model, sorted by score descending."""
    return await _list_prospects(session, model_id, page, per_page)


async def _list_prospects(
    session: AsyncSession,
    model_id: uuid.UUID,
    page: int = 1,
    per_page: int = 25,
) -> ProspectListResponse:
    """Shared helper to list prospects with pagination."""
    # Total count
    count_stmt = select(func.count()).select_from(Prospect).where(
        Prospect.icp_model_id == model_id
    )
    total = (await session.execute(count_stmt)).scalar() or 0

    # Paginated results sorted by score
    stmt = (
        select(Prospect)
        .where(Prospect.icp_model_id == model_id)
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
