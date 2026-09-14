from fastapi import APIRouter, Query, HTTPException
from app.services.soilnew import extract_transform_soil_data, extract_transform_soil_prob, load_to_postgres
from app.services.db import get_engine
from sqlalchemy import text
from app.core.config import settings
from app.schemas.soil import SoilPropertyResponse, SoilProbabilityResponse

router = APIRouter()

@router.get("/properties", response_model=list[dict])
def get_soil_properties(lat: float = Query(...), lon: float = Query(...)):
    engine = get_engine(settings.DB_USER, settings.DB_PASSWORD, settings.DB_NAME)

    result = None
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM soil_properties WHERE latitude = :lat AND longitude = :lon"),
                {"lat": lat, "lon": lon}
            ).fetchall()
    except Exception:
        pass  # DB missing/unreachable, fallback to fetching data

    if result:
        return [dict(row._mapping) for row in result]
    
    try:
        df_properties = extract_transform_soil_data(lat, lon)
        load_to_postgres(df_properties, "soil_properties", user=settings.DB_USER, password=settings.DB_PASSWORD, db_name=settings.DB_NAME)
        return df_properties.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/probabilities", response_model=list[dict])
def get_soil_probability(lat: float = Query(...), lon: float = Query(...)):
    engine = get_engine(settings.DB_USER, settings.DB_PASSWORD, settings.DB_NAME)

    result = None
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM soil_probabilities WHERE latitude = :lat AND longitude = :lon"),
                {"lat": lat, "lon": lon}
            ).fetchall()
    except Exception:
        pass  # DB missing/unreachable, fallback to fetching data

    if result:
        return [dict(row._mapping) for row in result]
    
    try:
        df_probabilities = extract_transform_soil_prob(lat, lon)
        load_to_postgres(df_probabilities, "soil_probabilities", user=settings.DB_USER, password=settings.DB_PASSWORD, db_name=settings.DB_NAME)
        return df_probabilities.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
