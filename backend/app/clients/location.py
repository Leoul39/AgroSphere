from typing import Dict, Any, Optional
import logging
from app.clients.base import BaseHTTPClient

logger = logging.getLogger(__name__)

class OSMClient(BaseHTTPClient):
    def __init__(self):
        super().__init__(base_url="https://nominatim.openstreetmap.org", timeout=10.0)
        self.headers = {
            "User-Agent": "AgroSphere/1.0 (Agriculture Decision Support System)"
        }

    async def reverse_geocode(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        url = "/reverse"
        params = {
            "lat": lat,
            "lon": lon,
            "format": "jsonv2"
        }
        
        try:
            data = await self.get(url, params=params, headers=self.headers)
            
            if data:
                return {
                    "input_coordinates": {"lat": lat, "lon": lon},
                    "formatted_city": data.get("display_name"),
                    "locational_info": data.get("address"),
                    "category": data.get("category"),
                    "type": data.get("type"),
                    "bounds_of_city": data.get("boundingbox"), # [lat_min, lat_max, lon_min, lon_max]
                    "center_of_city": {"lat": data.get("lat"), "lon": data.get("lon")}
                }
            return None
        except Exception as e:
            logger.error(f"Failed to reverse geocode with Nominatim: {e}")
            raise e

    async def forward_geocode(self, query: str) -> Optional[Dict[str, Any]]:
        url = "/search"
        params = {
            "q": query,
            "format": "jsonv2",
            "limit": 1
        }
        
        try:
            data = await self.get(url, params=params, headers=self.headers)
            
            if data and isinstance(data, list) and len(data) > 0:
                result = data[0]
                return {
                    "input_query": query,
                    "formatted_city": result.get("display_name"),
                    "bounds_of_city": result.get("boundingbox"),
                    "center_of_city": {"lat": result.get("lat"), "lon": result.get("lon")}
                }
            return None
        except Exception as e:
            logger.error(f"Failed to forward geocode with Nominatim: {e}")
            raise e

location_client = OSMClient()
