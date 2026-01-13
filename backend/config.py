import os
from pydantic import BaseModel

class Settings(BaseModel):
    APP_NAME: str = os.getenv("APP_NAME", "floatchat-backend")
    ENV: str = os.getenv("ENV", "dev")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/floatchat")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    VECTOR_DB_IMPL: str = os.getenv("VECTOR_DB_IMPL", "chroma")
    CHROMA_DIR: str = os.getenv("CHROMA_DIR", ".chroma")
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    MAX_ROWS: int = int(os.getenv("MAX_ROWS", "5000"))
    ALLOWED_FIELDS: str = os.getenv("ALLOWED_FIELDS", "temperature,salinity,pressure,latitude,longitude,datetime,float_id,platform_number")
    AUTH_TOKEN: str = os.getenv("AUTH_TOKEN", "dev-token")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "API KEy")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

settings = Settings()
