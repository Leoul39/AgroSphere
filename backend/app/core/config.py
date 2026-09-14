import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

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
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # External API Keys
    OPENCAGE_API_KEY: str = os.getenv("opencage_api_key", "")
    ISDA_USERNAME: str = os.getenv("ISDA_USERNAME", "")
    ISDA_PASSWORD: str = os.getenv("ISDA_PASSWORD", "")

settings = Settings()
