from typing import Optional
import logging
from app.clients.base import BaseHTTPClient

logger = logging.getLogger(__name__)

class OpenTopoDataClient(BaseHTTPClient):
    def __init__(self):
        super().__init__(base_url="https://api.opentopodata.org", timeout=10.0)

    async def get_elevation(self, lat: float, lon: float) -> Optional[float]:
        url = "/v1/srtm90m"
        params = {
            "locations": f"{lat},{lon}"
        }
        
        data = await self.get(url, params=params)
        
        if data and "results" in data and len(data["results"]) > 0:
            return data["results"][0].get("elevation")
        
        return None

elevation_client = OpenTopoDataClient()
