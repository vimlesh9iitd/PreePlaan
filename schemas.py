# ══════════════════════════════════════════════════════════════════
#  schemas.py  —  Pydantic request / response models
# ══════════════════════════════════════════════════════════════════

from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime


# ── Lecture ───────────────────────────────────────────────────────
class LectureSchema(BaseModel):
    title: str
    duration: str       # HH:MM:SS format


# ── DayPlan ───────────────────────────────────────────────────────
class DayPlanSchema(BaseModel):
    day: int
    lectures: List[LectureSchema]
    speedMultiplier: float = 1.0


# ── Create Plan Request ───────────────────────────────────────────
class CreatePlanRequest(BaseModel):
    id: Optional[str] = None         # Flutter sends its own UUID
    name: str = Field(default="My Study Plan", max_length=255)
    lectures: List[LectureSchema]
    dayPlans: List[DayPlanSchema]
    completedCount: int = 0
    speedMultiplier: float = 1.0
    hoursPerDay: int = 2
    createdAt: Optional[str] = None
    isActive: bool = False


# ── Update Progress Request ───────────────────────────────────────
class UpdateProgressRequest(BaseModel):
    completedCount: int


# ── Plan Response (what we send back to Flutter) ──────────────────
class PlanResponse(BaseModel):
    id: str
    name: str
    lectures: List[Any]
    dayPlans: List[Any]
    completedCount: int
    speedMultiplier: float
    hoursPerDay: int
    isActive: bool
    createdAt: str
    updatedAt: Optional[str] = None

    class Config:
        from_attributes = True


# ── Generic message ───────────────────────────────────────────────
class MessageResponse(BaseModel):
    message: str
    success: bool = True
