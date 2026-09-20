from fastapi import APIRouter, Query, HTTPException, Depends
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.analysis import AnalysisRepository
from app.clients.soil import soil_client
from app.clients.weather import weather_client
from app.clients.location import location_client
from app.clients.elevation import elevation_client
from app.services.llm import generate_soil_summary_with_gemini

router = APIRouter()

def check_land_use(soil_data, location_data) -> tuple[bool, str]:
    is_farmable = True
    reason = ""
    
    if isinstance(location_data, dict):
        loc_info = location_data.get("locational_info", {})
        country = loc_info.get("country", "Unknown Location")
        
        # Geofence to Ethiopia
        if "ethiopia" not in country.lower():
            return False, f"AgroSphere's current version is exclusively calibrated for agricultural analysis within Ethiopia (Detected: {country}). We cannot process coordinates in other countries at this time."

        loc_cat = location_data.get("category", "")
        loc_type = location_data.get("type", "")
        unfarmable_keywords = [
            "building", "commercial", "industrial", 
            "retail", "office", "water", "lake", "river", 
            "reservoir", "wetland", "ocean", "sea"
        ]
        if loc_cat in unfarmable_keywords or loc_type in unfarmable_keywords:
            return False, "This location appears to be an urban area, infrastructure, or a water body based on geographic data."
            
    if not soil_data or soil_data == "[]" or soil_data == [] or isinstance(soil_data, str):
        return False, "Please choose another location. We don't have soil data for deserts, waterbodies, and areas outside Africa."

    if isinstance(soil_data, list):
        if len(soil_data) == 0:
            return False, "Please choose another location. We don't have soil data for deserts, waterbodies, and areas outside Africa."
            
        for prop in soil_data:
            if isinstance(prop, dict) and prop.get("code") == "crop_cover_2019":
                mean_val = prop.get("mean")
                if mean_val is not None and float(mean_val) < 5.0:
                    return False, "This location appears to be barren, desert, or undisturbed natural land with <5% historical crop cover."
                break
                
    return is_farmable, reason

@router.get("/summary")
async def get_summary_info(
    lat: float = Query(...), 
    lon: float = Query(...),
    session: AsyncSession = Depends(get_db)
):
    try:
        repo = AnalysisRepository(session)
        
        # 1. Check Cache
        cached_analysis = await repo.get_cached_analysis(lat, lon)
        
        if cached_analysis:
            if cached_analysis.ai_summary:
                print("CACHE HIT! Returning stored AI summary.")
                return cached_analysis.ai_summary
            else:
                print("PARTIAL CACHE HIT! Generating AI summary from cached API data...")
                soil_data = cached_analysis.soil_data
                weather_summary = cached_analysis.weather_data
                location_data = cached_analysis.location_data
                elevation_data = cached_analysis.elevation_data
                
                is_farmable, unfarmable_reason = check_land_use(soil_data, location_data)
                
                summary = await generate_soil_summary_with_gemini(
                    str(soil_data), str(weather_summary), str(location_data), str(elevation_data), is_farmable, unfarmable_reason
                )
                
                await repo.update_ai_summary(lat, lon, summary)
                return summary
        else:
            print("CACHE MISS! Fetching from APIs...")
            # 2. Fetch all external data concurrently
            soil_task = soil_client.get_soil_properties(lat, lon)
            weather_task = weather_client.get_weather_summary(lat, lon)
            location_task = location_client.reverse_geocode(lat, lon)
            elevation_task = elevation_client.get_elevation(lat, lon)
            
            soil_res, weather_res, location_res, elevation_res = await asyncio.gather(
                soil_task, weather_task, location_task, elevation_task,
                return_exceptions=True
            )

            # Convert models to dicts for DB storage, or store error strings
            soil_data = [s.model_dump() for s in soil_res] if not isinstance(soil_res, Exception) else str(soil_res)
            weather_summary = weather_res.model_dump() if not isinstance(weather_res, Exception) else str(weather_res)
            location_data = location_res if not isinstance(location_res, Exception) else str(location_res)
            
            if isinstance(elevation_res, Exception) or elevation_res is None:
                elevation_data = None
            else:
                elevation_data = float(elevation_res)
            
            # 3. Check Land-Use
            is_farmable, unfarmable_reason = check_land_use(soil_data, location_data)
            
            if not is_farmable:
                # Fast-fail for unfarmable land (e.g. outside Ethiopia, oceans, cities)
                # Bypasses the 8-second Gemini generation time.
                summary = {
                    "is_farmable": False,
                    "unfarmable_reason": unfarmable_reason,
                    "general_location_summary": "Analysis aborted due to location constraints.",
                    "coordinate_specific_summary": "",
                    "climate_summary": "",
                    "soil_health_summary": "",
                    "recommended_crops": [],
                    "soil_amendments": [],
                    "risk_factors": [],
                    "irrigation_advice": ""
                }
            else:
                # 4. Generate AI Report BEFORE saving to Cache
                summary = await generate_soil_summary_with_gemini(
                    str(soil_data), str(weather_summary), str(location_data), str(elevation_data), is_farmable, unfarmable_reason
                )
            
            # 5. Save to Cache including the generated summary
            await repo.save_analysis(lat, lon, soil_data, weather_summary, elevation_data, location_data, summary)

            return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
