from fastapi import APIRouter, Query, HTTPException
from app.clients.soil import soil_client
from app.schemas.soil import SoilPropertyResponse

router = APIRouter()

@router.get("/properties", response_model=SoilPropertyResponse)
async def get_soil_properties(lat: float = Query(...), lon: float = Query(...)):
    properties = await soil_client.get_soil_properties(lat, lon)
    return SoilPropertyResponse(properties=properties)
