# ══════════════════════════════════════════════════════════════════
#  models.py  —  SQLAlchemy ORM Table Definitions
# ══════════════════════════════════════════════════════════════════

from sqlalchemy import (
    Column, String, Integer, Float, Boolean,
    DateTime, Text, ForeignKey, func
)
from sqlalchemy.dialects.postgresql import JSONB
from database import Base
import uuid


def generate_uuid():
    return str(uuid.uuid4())


class StudyPlan(Base):
    """
    One row = one study plan for one user.

    Columns:
      id              — UUID primary key
      user_id         — Supabase auth.users UUID (from JWT sub)
      name            — Plan name e.g. "OS Plan", "DBMS Plan"
      lectures        — JSON array of {title, duration}
      day_plans       — JSON array of day-wise schedule
      completed_count — How many lectures done
      speed_multiplier— e.g. 1.0 = normal, 2.0 = deep study
      hours_per_day   — daily study budget
      is_active       — only one plan active per user
      created_at      — auto timestamp
      updated_at      — auto update timestamp
    """
    __tablename__ = "study_plans"

    id               = Column(String, primary_key=True, default=generate_uuid)
    user_id          = Column(String, nullable=False, index=True)
    name             = Column(String(255), nullable=False, default="My Study Plan")
    lectures         = Column(JSONB, nullable=False, default=list)
    day_plans        = Column(JSONB, nullable=False, default=list)
    completed_count  = Column(Integer, nullable=False, default=0)
    speed_multiplier = Column(Float, nullable=False, default=1.0)
    hours_per_day    = Column(Integer, nullable=False, default=2)
    is_active        = Column(Boolean, nullable=False, default=False)
    created_at       = Column(DateTime(timezone=True), server_default=func.now())
    updated_at       = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
