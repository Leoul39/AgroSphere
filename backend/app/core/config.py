import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

# Load .env from the project root (AgroSphere/.env)
root_dir = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(root_dir / ".env")

class Settings(BaseModel):
    PROJECT_NAME: str = "AgroSphere API"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DB_USER: str = os.getenv("db_user", "postgres")
    DB_PASSWORD: str = os.getenv("db_password", "postgres")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "soil_info_db")
    
    @property
    def DATABASE_URL(self) -> str:
        url = os.getenv("DATABASE_URL")
        if url:
            return url
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        # Support converting both standard postgresql:// and psycopg2:// variants to asyncpg
        return self.DATABASE_URL.replace(
            "postgresql://", "postgresql+asyncpg://"
        ).replace(
            "postgresql+psycopg2://", "postgresql+asyncpg://"
        )
    
    # External API Keys
    OPENCAGE_API_KEY: str = os.getenv("opencage_api_key", "")
    ISDA_EMAIL: str = os.getenv("ISDA_EMAIL", "")
    ISDA_PASSWORD: str = os.getenv("ISDA_PASSWORD", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")

settings = Settings()
