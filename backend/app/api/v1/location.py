from fastapi import APIRouter, Query, HTTPException
from typing import Dict, Any, Optional
from app.clients.location import location_client

router = APIRouter()

@router.get("/reverse", response_model=Optional[Dict[str, Any]])
async def reverse_geocode(lat: float = Query(...), lon: float = Query(...)):
    """
    Given a latitude and longitude, returns the location details (city, region, bounding box).
    """
    try:
        return await location_client.reverse_geocode(lat, lon)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/forward", response_model=Optional[Dict[str, Any]])
async def forward_geocode(query: str = Query(..., description="Name of a city, region, or place")):
    """
    Given a text query, returns the coordinates and bounds of that place.
    """
    try:
        return await location_client.forward_geocode(query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
