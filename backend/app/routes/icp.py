"""ICP model CRUD routes and conversation endpoint."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_session
from app.models.icp import ICPModel
from app.schemas.icp import (
    ConversationRequest,
    ConversationResponse,
    DEFAULT_SCORING_WEIGHTS,
    ICPModelCreate,
    ICPModelResponse,
    ICPModelUpdate,
)

router = APIRouter(prefix="/api/icp", tags=["icp"])


@router.get("/", response_model=list[ICPModelResponse])
async def list_icp_models(
    is_active: bool | None = None,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(ICPModel)
    if is_active is not None:
        stmt = stmt.where(ICPModel.is_active == is_active)
    result = await session.execute(stmt)
    return result.scalars().all()


@router.post("/", response_model=ICPModelResponse, status_code=201)
async def create_icp_model(
    body: ICPModelCreate,
    session: AsyncSession = Depends(get_session),
):
    model = ICPModel(
        name=body.name,
        description=body.description,
        criteria=body.criteria,
        scoring_weights=body.scoring_weights,
        version="1.0",
    )
    session.add(model)
    await session.commit()
    await session.refresh(model)
    return model


@router.get("/{model_id}", response_model=ICPModelResponse)
async def get_icp_model(
    model_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    model = await session.get(ICPModel, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="ICP model not found")
    return model


@router.patch("/{model_id}", response_model=ICPModelResponse)
async def update_icp_model(
    model_id: uuid.UUID,
    body: ICPModelUpdate,
    session: AsyncSession = Depends(get_session),
):
    model = await session.get(ICPModel, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="ICP model not found")

    updates = body.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(model, field, value)

    await session.commit()
    await session.refresh(model)
    return model


@router.post("/{model_id}/activate", response_model=ICPModelResponse)
async def activate_icp_model(
    model_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    model = await session.get(ICPModel, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="ICP model not found")

    # Deactivate all other models
    all_models = await session.execute(select(ICPModel))
    for m in all_models.scalars():
        m.is_active = False

    model.is_active = True
    await session.commit()
    await session.refresh(model)
    return model


@router.post("/conversation", response_model=ConversationResponse)
async def conversation(
    body: ConversationRequest,
    session: AsyncSession = Depends(get_session),
):
    """Send a message describing your ideal customer; Claude extracts a structured ICP."""
    from agents.icp_architect.agent import ICPArchitect

    if not settings.anthropic_api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not configured")

    agent = ICPArchitect(api_key=settings.anthropic_api_key, model=settings.claude_model)
    result = await agent.run(message=body.message)

    if "error" in result:
        raise HTTPException(status_code=502, detail=result["error"])

    # Persist the extracted ICP
    model = ICPModel(
        name=result.get("name", "Untitled ICP"),
        description=result.get("description"),
        criteria=result.get("criteria", {}),
        scoring_weights=DEFAULT_SCORING_WEIGHTS.copy(),
        version="1.0",
    )
    session.add(model)
    await session.commit()
    await session.refresh(model)

    return ConversationResponse(
        icp_model=ICPModelResponse.model_validate(model),
        follow_up_questions=result.get("follow_up_questions", []),
    )
