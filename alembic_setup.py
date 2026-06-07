# ══════════════════════════════════════════════════════════════════
#  alembic_setup.py
#  
#  Run this ONCE to create the DB table automatically.
#  Alembic use nahi karna? Direct SQL bhi neeche diya hai.
# ══════════════════════════════════════════════════════════════════

"""
OPTION A — SQLAlchemy se auto-create (recommended for first deploy):
    python alembic_setup.py

OPTION B — Supabase SQL Editor mein ye SQL run karo manually:

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS study_plans (
    id               TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id          TEXT NOT NULL,
    name             VARCHAR(255) NOT NULL DEFAULT 'My Study Plan',
    lectures         JSONB NOT NULL DEFAULT '[]',
    day_plans        JSONB NOT NULL DEFAULT '[]',
    completed_count  INTEGER NOT NULL DEFAULT 0,
    speed_multiplier DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    hours_per_day    INTEGER NOT NULL DEFAULT 2,
    is_active        BOOLEAN NOT NULL DEFAULT FALSE,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    updated_at       TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast user-based queries
CREATE INDEX IF NOT EXISTS idx_study_plans_user_id ON study_plans(user_id);

-- Auto-update updated_at on row change
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE OR REPLACE TRIGGER update_study_plans_updated_at
    BEFORE UPDATE ON study_plans
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (IMPORTANT for Supabase)
ALTER TABLE study_plans ENABLE ROW LEVEL SECURITY;

-- Users can only see their own plans
CREATE POLICY "Users can view own plans" ON study_plans
    FOR SELECT USING (auth.uid()::text = user_id);

CREATE POLICY "Users can insert own plans" ON study_plans
    FOR INSERT WITH CHECK (auth.uid()::text = user_id);

CREATE POLICY "Users can update own plans" ON study_plans
    FOR UPDATE USING (auth.uid()::text = user_id);

CREATE POLICY "Users can delete own plans" ON study_plans
    FOR DELETE USING (auth.uid()::text = user_id);
"""

import asyncio
from database import engine, Base
from models import StudyPlan  # noqa: F401 — import so table is registered


async def create_tables():
    print("Creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables created successfully!")


if __name__ == "__main__":
    asyncio.run(create_tables())
