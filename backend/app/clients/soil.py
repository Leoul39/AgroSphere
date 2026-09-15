from typing import List, Dict, Any, Optional
import os
import logging
import asyncio
from datetime import datetime, timedelta
from fastapi import HTTPException
from app.clients.base import BaseHTTPClient
from app.schemas.soil import SoilPropertyBase

logger = logging.getLogger(__name__)

class ISDAClient(BaseHTTPClient):
    def __init__(self):
        super().__init__(base_url="https://api.isda-africa.com", timeout=20.0)
        self._access_token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None

    async def _ensure_token(self):
        """Fetches a new access token if it is missing or about to expire in less than 5 minutes."""
        if not self._access_token or not self._token_expiry or datetime.now() >= (self._token_expiry - timedelta(minutes=5)):
            from app.core.config import settings
            username = settings.ISDA_EMAIL
            password = settings.ISDA_PASSWORD
            
            if not username or not password:
                raise HTTPException(status_code=500, detail="ISDA credentials are not configured in the environment variables.")
                
            payload = {"username": username, "password": password}
            try:
                # Use a raw httpx request for auth to bypass the BaseHTTPClient retry/auth injection loop
                import httpx
                async with httpx.AsyncClient(timeout=15.0) as client:
                    resp = await client.post(f"{self.base_url}/login", data=payload)
                    resp.raise_for_status()
                    token_data = resp.json()
                    self._access_token = token_data.get("access_token")
                    self._token_expiry = datetime.now() + timedelta(minutes=60)
                    logger.info("Successfully fetched fresh ISDA access token.")
            except Exception as e:
                logger.error(f"Failed to authenticate with ISDA API: {e}")
                raise HTTPException(status_code=502, detail="Failed to authenticate with ISDA API")

    async def get_soil_properties(self, lat: float, lon: float) -> List[SoilPropertyBase]:
        await self._ensure_token()
        
        headers = {"Authorization": f"Bearer {self._access_token}"}
        params = {"lat": lat, "lon": lon}
        
        # ISDA handles 401 Unauthorized internally if token is invalid, but our _ensure_token handles freshness.
        data = await self.get("/isdasoil/v2/soilproperty", params=params, headers=headers)
        
        records = []
        properties = data.get("property", {})
        
        for prop_code, depth_list in properties.items():
            for depth_item in depth_list:
                value_info = depth_item.get("value", {})
                depth_info = depth_item.get("depth", {})
                
                mean_val = value_info.get("value")
                unit = str(value_info.get("unit") or "")
                depth_val = depth_info.get("value")
                depth_unit = depth_info.get("unit")
                
                if mean_val is not None:
                    records.append(SoilPropertyBase(
                        code=prop_code,
                        name=prop_code.replace("_", " ").title(),
                        mapped_units=unit,
                        target_units=unit,
                        depth_label=f"{depth_val}{depth_unit}",
                        mean=mean_val
                    ))
                    
        if not records:
            # ISDA returns empty if coordinates are outside Africa or in water bodies
            raise ValueError("ISDA API returned no soil data. Make sure coordinates are within Africa and not in water/deserts.")
            
        return records

soil_client = ISDAClient()
