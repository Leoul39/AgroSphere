from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta, timezone
from app.models.analysis import AnalysisCache

class AnalysisRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _get_location_key(self, lat: float, lon: float) -> str:
        # Round to 3 decimal places (~110m resolution at equator)
        return f"{lat:.3f}_{lon:.3f}"

    async def get_cached_analysis(self, lat: float, lon: float) -> Optional[AnalysisCache]:
        location_key = self._get_location_key(lat, lon)
        stmt = select(AnalysisCache).where(AnalysisCache.location_key == location_key)
        result = await self.session.execute(stmt)
        record = result.scalars().first()
        
        if record:
            # Check if cache is expired
            if record.expires_at > datetime.now(timezone.utc):
                return record
            else:
                # Optional: Delete expired record, or just overwrite it later
                await self.session.delete(record)
                await self.session.commit()
                
        return None

    async def save_analysis(
        self, 
        lat: float, 
        lon: float, 
        soil_data: list, 
        weather_data: dict, 
        elevation_data: float,
        location_data: dict,
        ai_summary: str
    ) -> AnalysisCache:
        location_key = self._get_location_key(lat, lon)
        
        # Weather data changes fastest, expire in 24 hours
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        
        new_cache = AnalysisCache(
            location_key=location_key,
            lat=lat,
            lon=lon,
            soil_data=soil_data,
            weather_data=weather_data,
            elevation_data=elevation_data,
            location_data=location_data,
            ai_summary=ai_summary,
            expires_at=expires_at
        )
        
        self.session.add(new_cache)
        await self.session.commit()
        await self.session.refresh(new_cache)
        return new_cache

    async def update_ai_summary(self, lat: float, lon: float, ai_summary: str):
        location_key = self._get_location_key(lat, lon)
        stmt = select(AnalysisCache).where(AnalysisCache.location_key == location_key)
        result = await self.session.execute(stmt)
        record = result.scalars().first()
        if record:
            record.ai_summary = ai_summary
            await self.session.commit()
