from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

import os

# Set all CORS enabled origins
frontend_url = os.getenv("FRONTEND_URL", "https://agrosphere.vercel.app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5173",
        "https://agro-sphere-gilt.vercel.app",
        "https://agro-sphere-47zfzagqq-leoul.vercel.app",
        frontend_url
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "Welcome to the AgroSphere API. Go to /docs for the API documentation."}
