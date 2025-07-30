from fastapi import FastAPI, Query
from soilnew import extract_transform_soil_data, extract_transform_soil_prob, load_to_postgres
from db import get_engine
from sqlalchemy import text
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from isda import fetch_isda_soil_property
from weather import fetch_weather_open, summarize_weather_dataframe
from location import reverse_geocode
from elevation import get_elevation
from llm import generate_soil_summary_with_gemini

load_dotenv()

app = FastAPI()

# Replace with your actual credentials or load from .env
DB_USER = os.getenv('db_user')
DB_PASS = os.getenv('db_password')
DB_NAME = "soil_info_db"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/soil_properties/")
def get_soil_properties(lat: float = Query(...), lon: float = Query(...)):
    engine = get_engine(DB_USER, DB_PASS, DB_NAME)

    # Check if this coordinate is already in DB
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM soil_properties WHERE latitude = :lat AND longitude = :lon"),
            {"lat": lat, "lon": lon}
        ).fetchall()

    # If data exists, return it
    if result:
        return [dict(row._mapping) for row in result]
    
    # Otherwise: extract → transform → load → return
    df_properties = extract_transform_soil_data(lat, lon)

    # Save to DB
    load_to_postgres(df_properties, "soil_properties", user=DB_USER, password=DB_PASS, db_name=DB_NAME)

    return df_properties.to_dict(orient="records")

@app.get("/soil_probability/")
def get_soil_probability(lat: float = Query(...), lon: float = Query(...)):
    engine = get_engine(DB_USER, DB_PASS, DB_NAME)

    # Check if this coordinate is already in DB
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM soil_probabilities WHERE latitude = :lat AND longitude = :lon"),
            {"lat": lat, "lon": lon}
        ).fetchall()

    # If data exists, return it
    if result:
        return [dict(row._mapping) for row in result]
    
    # Otherwise: extract → transform → load → return
    df_probabilities = extract_transform_soil_prob(lat, lon)

    # Save to DB
    load_to_postgres(df_probabilities, "soil_probabilities", user=DB_USER, password=DB_PASS, db_name=DB_NAME)

    return df_probabilities.to_dict(orient="records")


@app.get("/summary_info/")
async def get_summary_info(lat: float = Query(...), lon: float = Query(...)):
    # Await async functions directly
    soil_data = await fetch_isda_soil_property(lat, lon)
    
    # These may be sync functions – call normally if so
    weather = fetch_weather_open(lat, lon)
    weather_summary = summarize_weather_dataframe(weather)
    location_data = reverse_geocode(lat, lon)
    elevation_data = get_elevation(lat, lon)

    # Call Gemini LLM generator
    summary = generate_soil_summary_with_gemini(
        soil_data, weather_summary, location_data, elevation_data
    )

    return summary

        
