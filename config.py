from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    supabase_jwt_secret: str
    supabase_url: str = ""
    supabase_anon_key: str = ""

    model_config = {"env_file": ".env"}

settings = Settings()
