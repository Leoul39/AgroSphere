from fastapi import APIRouter
from app.api.v1 import health, soil, analyses, location

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(location.router, prefix="/location", tags=["location"])
api_router.include_router(soil.router, prefix="/soil", tags=["soil"])
api_router.include_router(analyses.router, prefix="/analyses", tags=["analyses"])
