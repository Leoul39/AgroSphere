import httpx
import json
import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Weather code interpretation for the open meteo API
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Thunderstorm with heavy hail"
}

def fetch_weather_open(lat: float, lon: float):
    """
    Fetches historical and forecasted weather data for a given latitude and longitude from Open-Meteo.

    Open-Meteo is an open-source weather API and offers free access for non-commercial use. No API key required.

    Args:
        lat - latitude of the coordinate
        lon - longitude of the coordinate

    Returns:
        pd.DataFrame: A DataFrame containing hourly weather data with columns:
            - datetime: Timestamp in Africa/Nairobi timezone
            - temperature (°C): Hourly temperature in degrees Celsius
            - humidity (%): Hourly relative humidity in percentage
            - precipitation (mm): Hourly precipitation in millimeters
            - weather_code: Numerical code representing the weather condition
            - weather_summary: Textual description of the weather condition
            - Season_et: Ethiopian season based on the month
            - Season_en: English season based on the month
            
    """
    # Define dates
    today = datetime.now().date()
    start_past = today - timedelta(days=7)
    end_past = today - timedelta(days=1)  # Archive excludes today
    future_days = 7  # today + 6 days forecast

    # Historical API (archive)
    url_past = (
        f"https://historical-forecast-api.open-meteo.com/v1/archive?"
        f"latitude={lat}&longitude={lon}"
        f"&start_date={start_past}&end_date={end_past}"
        f"&hourly=temperature_2m,relative_humidity_2m,precipitation,weathercode"
        f"&timezone=Africa%2FNairobi"
    )

    # Forecast API (today + next 6 days)
    url_future = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&forecast_days={future_days}&hourly=temperature_2m,relative_humidity_2m,precipitation,weathercode"
        f"&timezone=Africa%2FNairobi"
    )

    # Fetch past
    resp_past = requests.get(url_past)
    df_past = pd.DataFrame()
    if resp_past.status_code == 200:
        data = resp_past.json()
        df_past = pd.DataFrame({
            "datetime": data["hourly"]["time"],
            "temperature (°C)": data["hourly"]["temperature_2m"],
            "humidity (%)": data["hourly"]["relative_humidity_2m"],
            "precipitation (mm)": data["hourly"]["precipitation"],
            "weather_code": data["hourly"]["weathercode"],
        })

    # Fetch forecast
    resp_future = requests.get(url_future)
    df_future = pd.DataFrame()
    if resp_future.status_code == 200:
        data = resp_future.json()
        df_future = pd.DataFrame({
            "datetime": data["hourly"]["time"],
            "temperature (°C)": data["hourly"]["temperature_2m"],
            "humidity (%)": data["hourly"]["relative_humidity_2m"],
            "precipitation (mm)": data["hourly"]["precipitation"],
            "weather_code": data["hourly"]["weathercode"],
        })

    # Combine both
    df_all = pd.concat([df_past, df_future], ignore_index=True)

    # Convert to datetime with timezone
    df_all['datetime'] = pd.to_datetime(df_all['datetime']).dt.tz_localize('Africa/Nairobi')

    # Map weather code to readable label
    df_all['weather_summary'] = df_all['weather_code'].map(WEATHER_CODES)

    # Function to get the Ethiopian seasons 
    def get_season_et(month: int) -> str:
        if month in [12, 1, 2]:  
            return "Bega"
        elif month in [3, 4, 5]:  
            return "Belg"
        elif month in [6, 7, 8]:  
            return "Kiremt"
        elif month in [9, 10, 11]:
            return "Tsedey"
        return "Unknown"
    
    # Function to get the English seasons
    def get_season_en(month: int) -> str:
        if month in [12, 1, 2]:
            return "Winter"
        elif month in [3, 4, 5]:
            return "Spring"
        elif month in [6, 7, 8]:
            return "Summer"
        elif month in [9, 10, 11]:
            return "Autumn"
        return "Unknown"
    
    # Extract month and map to Ethiopian and English seasons
    df_all["month"] = df_all["datetime"].dt.month
    df_all["Season_et"] = df_all["month"].apply(get_season_et)
    df_all["Season_en"] = df_all["month"].apply(get_season_en)

    # Drop the month column as it's no longer needed
    df_all.drop(columns=["month"], inplace=True)

    # Add lat/lon
    df_all['latitude'] = lat
    df_all['longitude'] = lon

    return df_all

def summarize_weather_dataframe(df):
    """
    Summarizes historical and forecasted weather data for a given location.

    Extracts average temperature, humidity, total rainfall, and rainy day count
    across the entire DataFrame period. It also includes today's specific weather 
    and determines the Ethiopian and English seasons based on today's date.

    Args:
        df (pd.DataFrame): A weather DataFrame containing hourly records with 
            temperature, humidity, precipitation, and season columns.

    Returns:
        dict: A summary dictionary with start/end dates, seasonal info,
              average weather stats, rainy day count, and today's conditions.
    """
    # Extract date from datetime
    df["date"] = df["datetime"].dt.date

    # Get today
    today = datetime.now().date()

    # Summary range
    start_date = df["date"].min()
    end_date = df["date"].max()

    # Aggregate daily stats
    daily_avg = df.groupby("date").agg({
        "temperature (°C)": "mean",
        "humidity (%)": "mean",
        "precipitation (mm)": "sum"
    }).reset_index()

    # Overall stats
    avg_temp = round(daily_avg["temperature (°C)"].mean(), 1)
    avg_humidity = round(daily_avg["humidity (%)"].mean(), 1)
    total_rain = round(daily_avg["precipitation (mm)"].sum(), 1)
    rainy_days = (daily_avg["precipitation (mm)"] > 1.0).sum()

    today_row = df[df["datetime"].dt.date == today]

    # Safely extract season values
    season_et = today_row["Season_et"].iloc[0] if not today_row.empty else "Unknown"
    season_en = today_row["Season_en"].iloc[0] if not today_row.empty else "Unknown"

    # Today's weather (if available)
    today_data = df[df["date"] == today]
    if not today_data.empty:
        today_temp = round(today_data["temperature (°C)"].mean(), 1)
        today_humidity = round(today_data["humidity (%)"].mean(), 1)
        today_precip = round(today_data["precipitation (mm)"].sum(), 1)
    else:
        today_temp = today_humidity = today_precip = "N/A"

    return {
        "start_date": str(start_date),
        "today_date": str(today),
        "end_date": str(end_date),
        "season_et": season_et,
        "season_en": season_en,
        "avg_temperature": f"{avg_temp} °C",
        "avg_humidity": f"{avg_humidity}%",
        "total_precipitation": f"{total_rain} mm",
        "rainy_days": int(rainy_days),
        "today_weather": {
            "temperature": f"{today_temp} °C",
            "humidity": f"{today_humidity}%",
            "precipitation": f"{today_precip} mm"
        }
    }

if __name__ == "__main__":
    # Example usage
    lat = 9.145
    lon = 40.489673
    weather_data = fetch_weather_open(lat, lon)
    print(weather_data.head())