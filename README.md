# Pree Plaan — FastAPI Backend

New backend for Pree Plaan app.
HF OCR backend alag hai aur UNTOUCHED hai.
Yeh backend sirf plan storage handle karta hai.

---

## Folder Structure

```
pree_plaan_backend/
├── main.py            ← FastAPI app entry point
├── database.py        ← Async SQLAlchemy + Supabase DB connection
├── config.py          ← Environment variables
├── models.py          ← ORM table: study_plans
├── schemas.py         ← Pydantic request/response models
├── auth.py            ← Supabase JWT verification
├── alembic_setup.py   ← DB table create karo / SQL script
├── requirements.txt   ← Python packages
├── .env.example       ← Env template (apna .env banao isse)
└── routes/
    └── plans.py       ← All /plans API endpoints
```

---

## Step 1 — Supabase Setup

### 1.1 — Google OAuth Enable karo
1. Supabase Dashboard → Authentication → Providers → Google → Enable
2. Google Cloud Console mein OAuth credentials banao
3. Client ID + Secret Supabase mein daalo
4. Redirect URL add karo: `https://YOUR_PROJECT.supabase.co/auth/v1/callback`

### 1.2 — Database Table banao
Supabase Dashboard → SQL Editor mein yeh SQL run karo:

```sql
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

CREATE INDEX IF NOT EXISTS idx_study_plans_user_id ON study_plans(user_id);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_study_plans_updated_at
    BEFORE UPDATE ON study_plans
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE study_plans ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own plans" ON study_plans
    FOR SELECT USING (auth.uid()::text = user_id);
CREATE POLICY "Users can insert own plans" ON study_plans
    FOR INSERT WITH CHECK (auth.uid()::text = user_id);
CREATE POLICY "Users can update own plans" ON study_plans
    FOR UPDATE USING (auth.uid()::text = user_id);
CREATE POLICY "Users can delete own plans" ON study_plans
    FOR DELETE USING (auth.uid()::text = user_id);
```

### 1.3 — Credentials collect karo
| Value | Kahan milega |
|---|---|
| `DATABASE_URL` | Supabase → Settings → Database → URI |
| `SUPABASE_JWT_SECRET` | Supabase → Settings → API → JWT Secret |
| `SUPABASE_URL` | Supabase → Settings → API → Project URL |
| `SUPABASE_ANON_KEY` | Supabase → Settings → API → anon public |

---

## Step 2 — Local Setup

```bash
# 1. Folder mein jao
cd pree_plaan_backend

# 2. Virtual environment banao
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Packages install karo
pip install -r requirements.txt

# 4. .env file banao
cp .env.example .env
# ab .env open karo aur apni values daalo

# 5. Server run karo
uvicorn main:app --reload --port 8000
```

Server chal gaya to open karo:
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

---

## Step 3 — Flutter mein URL update karo

`main.dart` mein yeh line update karo:

```dart
// LOCAL testing ke liye:
const String newApiUrl = 'http://10.0.2.2:8000';   // Android emulator
const String newApiUrl = 'http://localhost:8000';    // iOS simulator

// Production deploy ke baad:
const String newApiUrl = 'https://your-deployed-url.com';
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/plans` | Saare plans load karo |
| POST | `/plans` | Naya plan save karo |
| GET | `/plans/{id}` | Ek plan detail |
| PATCH | `/plans/{id}/progress` | Progress update karo |
| PATCH | `/plans/{id}/activate` | Plan ko active karo |
| DELETE | `/plans/{id}` | Plan delete karo |

Har request mein header chahiye:
```
Authorization: Bearer <supabase_access_token>
```
Flutter Supabase SDK automatically ye token bhejta hai.

---

## Step 4 — Production Deploy (Free Options)

### Option A — Railway.app (Recommended, Easy)
```bash
# railway.app pe account banao
# GitHub repo connect karo
# Environment variables add karo (same as .env)
# Deploy!
```

### Option B — Render.com (Free tier available)
1. render.com pe Web Service banao
2. GitHub repo connect karo
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Environment variables set karo

### Option C — Fly.io
```bash
brew install flyctl
flyctl auth login
flyctl launch
flyctl secrets set DATABASE_URL="..." SUPABASE_JWT_SECRET="..."
flyctl deploy
```

---

## Auth Flow (Kaise kaam karta hai)

```
Flutter App
    ↓ Google Login (Supabase)
    ↓ Supabase deta hai access_token (JWT)
    ↓
FastAPI Backend
    ↓ Authorization: Bearer <token> header check karta hai
    ↓ JWT verify karta hai (Supabase JWT Secret se)
    ↓ user_id (sub claim) nikalte hain
    ↓ Sirf us user ke plans return karta hai
```

---

## HF OCR Backend Status

```
HF OCR Backend (https://vimleshiit4463-pythonback.hf.space)
    ✅ UNTOUCHED — koi change nahi hua
    ✅ Flutter abhi bhi directly call karta hai
    ✅ baseUrl constant wahi hai

New FastAPI Backend
    ✅ ALAG server
    ✅ Sirf plan storage
    ✅ newApiUrl constant alag hai
```

Dono backends simultaneously chalte hain, koi conflict nahi.
