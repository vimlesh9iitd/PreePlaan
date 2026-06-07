# ══════════════════════════════════════════════════════════════════
#  config.py  —  Environment variables (.env se load hoga)
# ══════════════════════════════════════════════════════════════════

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ── Supabase ─────────────────────────────────────────────────
    # Supabase Dashboard → Settings → Database → Connection String (URI)
    database_url: str

    # Supabase JWT Secret
    # Supabase Dashboard → Settings → API → JWT Secret
    supabase_jwt_secret: str

    # Supabase Project URL & Anon Key (optional, for admin tasks)
    supabase_url: str = ""
    supabase_anon_key: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
