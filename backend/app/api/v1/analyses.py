from fastapi import APIRouter, Query, HTTPException
from app.services.isda import fetch_isda_soil_property
from app.services.weather import fetch_weather_open, summarize_weather_dataframe
from app.services.location import reverse_geocode
from app.services.elevation import get_elevation
from app.services.llm import generate_soil_summary_with_gemini

router = APIRouter()

@router.get("/summary")
async def get_summary_info(lat: float = Query(...), lon: float = Query(...)):
    try:
        soil_data = await fetch_isda_soil_property(lat, lon)
        
        weather = fetch_weather_open(lat, lon)
        weather_summary = summarize_weather_dataframe(weather)
        location_data = reverse_geocode(lat, lon)
        elevation_data = get_elevation(lat, lon)

        summary = generate_soil_summary_with_gemini(
            soil_data, weather_summary, location_data, elevation_data
        )
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
