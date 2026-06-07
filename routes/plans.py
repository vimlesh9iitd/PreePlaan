# ══════════════════════════════════════════════════════════════════
#  routes/plans.py  —  All /plans endpoints
#
#  GET    /plans            → user ke saare plans
#  POST   /plans            → naya plan save
#  GET    /plans/{id}       → ek plan detail
#  DELETE /plans/{id}       → plan delete
#  PATCH  /plans/{id}/progress  → progress update
#  PATCH  /plans/{id}/activate  → set as active plan
# ══════════════════════════════════════════════════════════════════

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List
import uuid
from datetime import datetime, timezone

from database import get_db
from models import StudyPlan
from schemas import (
    CreatePlanRequest,
    UpdateProgressRequest,
    PlanResponse,
    MessageResponse,
)
from auth import get_current_user

router = APIRouter()


# ── Helper: ORM → response dict ──────────────────────────────────
def plan_to_response(plan: StudyPlan) -> dict:
    return {
        "id": plan.id,
        "name": plan.name,
        "lectures": plan.lectures,
        "dayPlans": plan.day_plans,
        "completedCount": plan.completed_count,
        "speedMultiplier": plan.speed_multiplier,
        "hoursPerDay": plan.hours_per_day,
        "isActive": plan.is_active,
        "createdAt": plan.created_at.isoformat() if plan.created_at else datetime.now(timezone.utc).isoformat(),
        "updatedAt": plan.updated_at.isoformat() if plan.updated_at else None,
    }


# ══════════════════════════════════════════════════════════════════
# GET /plans  — Load all plans for current user
# ══════════════════════════════════════════════════════════════════
@router.get("", response_model=List[PlanResponse])
async def get_all_plans(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    result = await db.execute(
        select(StudyPlan)
        .where(StudyPlan.user_id == user_id)
        .order_by(StudyPlan.created_at.desc())
    )
    plans = result.scalars().all()
    return [plan_to_response(p) for p in plans]


# ══════════════════════════════════════════════════════════════════
# POST /plans  — Save a new plan
# ══════════════════════════════════════════════════════════════════
@router.post("", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(
    body: CreatePlanRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    # Agar yeh pehla plan hai to auto-activate
    existing_result = await db.execute(
        select(StudyPlan).where(StudyPlan.user_id == user_id)
    )
    existing_plans = existing_result.scalars().all()
    is_first_plan = len(existing_plans) == 0

    # Agar body mein isActive=True hai to pehle sab deactivate karo
    if body.isActive or is_first_plan:
        await db.execute(
            update(StudyPlan)
            .where(StudyPlan.user_id == user_id)
            .values(is_active=False)
        )

    # Created at parse karo
    try:
        created_at = datetime.fromisoformat(body.createdAt) if body.createdAt else datetime.now(timezone.utc)
    except Exception:
        created_at = datetime.now(timezone.utc)

    new_plan = StudyPlan(
        id=body.id or str(uuid.uuid4()),
        user_id=user_id,
        name=body.name,
        lectures=[l.model_dump() for l in body.lectures],
        day_plans=[
            {
                "day": d.day,
                "lectures": [l.model_dump() for l in d.lectures],
                "speedMultiplier": d.speedMultiplier,
            }
            for d in body.dayPlans
        ],
        completed_count=body.completedCount,
        speed_multiplier=body.speedMultiplier,
        hours_per_day=body.hoursPerDay,
        is_active=body.isActive or is_first_plan,
        created_at=created_at,
    )

    db.add(new_plan)
    await db.flush()
    await db.refresh(new_plan)
    return plan_to_response(new_plan)


# ══════════════════════════════════════════════════════════════════
# GET /plans/{plan_id}  — Get single plan
# ══════════════════════════════════════════════════════════════════
@router.get("/{plan_id}", response_model=PlanResponse)
async def get_plan(
    plan_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    result = await db.execute(
        select(StudyPlan)
        .where(StudyPlan.id == plan_id, StudyPlan.user_id == user_id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan nahi mila")
    return plan_to_response(plan)


# ══════════════════════════════════════════════════════════════════
# PATCH /plans/{plan_id}/progress  — Update completed count
# ══════════════════════════════════════════════════════════════════
@router.patch("/{plan_id}/progress", response_model=PlanResponse)
async def update_progress(
    plan_id: str,
    body: UpdateProgressRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    result = await db.execute(
        select(StudyPlan)
        .where(StudyPlan.id == plan_id, StudyPlan.user_id == user_id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan nahi mila")

    # Validate completed count
    total_lectures = len(plan.lectures) if plan.lectures else 0
    if body.completedCount < 0 or body.completedCount > total_lectures:
        raise HTTPException(
            status_code=400,
            detail=f"completedCount must be between 0 and {total_lectures}",
        )

    plan.completed_count = body.completedCount
    await db.flush()
    await db.refresh(plan)
    return plan_to_response(plan)


# ══════════════════════════════════════════════════════════════════
# PATCH /plans/{plan_id}/activate  — Set as active plan
# ══════════════════════════════════════════════════════════════════
@router.patch("/{plan_id}/activate", response_model=PlanResponse)
async def activate_plan(
    plan_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    # Pehle check: plan exist karta hai?
    result = await db.execute(
        select(StudyPlan)
        .where(StudyPlan.id == plan_id, StudyPlan.user_id == user_id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan nahi mila")

    # Sab deactivate karo
    await db.execute(
        update(StudyPlan)
        .where(StudyPlan.user_id == user_id)
        .values(is_active=False)
    )

    # Sirf yeh plan activate karo
    plan.is_active = True
    await db.flush()
    await db.refresh(plan)
    return plan_to_response(plan)


# ══════════════════════════════════════════════════════════════════
# DELETE /plans/{plan_id}  — Delete a plan
# ══════════════════════════════════════════════════════════════════
@router.delete("/{plan_id}", response_model=MessageResponse)
async def delete_plan(
    plan_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    result = await db.execute(
        select(StudyPlan)
        .where(StudyPlan.id == plan_id, StudyPlan.user_id == user_id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan nahi mila")

    await db.delete(plan)

    # Agar deleted plan active tha to latest plan ko active kar do
    if plan.is_active:
        latest_result = await db.execute(
            select(StudyPlan)
            .where(StudyPlan.user_id == user_id)
            .order_by(StudyPlan.created_at.desc())
            .limit(1)
        )
        latest = latest_result.scalar_one_or_none()
        if latest:
            latest.is_active = True

    return {"message": f"Plan '{plan.name}' delete ho gaya", "success": True}
