# ══════════════════════════════════════════════════════════════════
#  PREE PLAAN — New FastAPI Backend
#  🗄️  Supabase PostgreSQL  |  🔐 Supabase JWT Auth
#
#  HF OCR backend is SEPARATE and UNTOUCHED.
#  This backend ONLY handles:
#    - Plan CRUD  (save / load / delete)
#    - Progress update
#    - Set active plan
#
#  Run:  uvicorn main:app --reload --port 8000
# ══════════════════════════════════════════════════════════════════

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from database import engine, Base
from routes import plans

# ── Create tables on startup ──────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title="Pree Plaan API",
    description="Backend for Pree Plaan study planner app",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS — allow Flutter app ──────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # production mein apna domain dalna
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────
app.include_router(plans.router, prefix="/plans", tags=["Plans"])

@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "Pree Plaan Backend Running ✅"}

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
