from sqlalchemy import Column, Float, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import BaseModel

class AnalysisCache(BaseModel):
    __tablename__ = "analysis_cache"

    # We use a combined string key for the rounded coordinates to ensure uniqueness
    # Format: "lat_lon", e.g., "9.680_36.680"
    location_key = Column(String, unique=True, index=True, nullable=False)
    
    # Store exact requested coordinates for reference
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    
    soil_data = Column(JSONB, nullable=True)
    weather_data = Column(JSONB, nullable=True)
    elevation_data = Column(Float, nullable=True)
    location_data = Column(JSONB, nullable=True)
    ai_summary = Column(String, nullable=True)
    
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
