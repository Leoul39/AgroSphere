from typing import Dict, Any
from datetime import datetime, timedelta
import asyncio
import pandas as pd
import logging
from app.clients.base import BaseHTTPClient
from app.schemas.weather import WeatherSummary

logger = logging.getLogger(__name__)

WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog", 51: "Light drizzle", 53: "Moderate drizzle",
    55: "Dense drizzle", 56: "Light freezing drizzle", 57: "Dense freezing drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain", 66: "Light freezing rain",
    67: "Heavy freezing rain", 71: "Slight snow fall", 73: "Moderate snow fall",
    75: "Heavy snow fall", 77: "Snow grains", 80: "Slight rain showers",
    81: "Moderate rain showers", 82: "Violent rain showers", 85: "Slight snow showers",
    86: "Heavy snow showers", 95: "Thunderstorm", 96: "Thunderstorm with hail",
    99: "Thunderstorm with heavy hail"
}

def get_season_et(month: int) -> str:
    if month in [12, 1, 2]: return "Bega"
    elif month in [3, 4, 5]: return "Belg"
    elif month in [6, 7, 8]: return "Kiremt"
    elif month in [9, 10, 11]: return "Tsedey"
    return "Unknown"

def get_season_en(month: int) -> str:
    if month in [12, 1, 2]: return "Winter"
    elif month in [3, 4, 5]: return "Spring"
    elif month in [6, 7, 8]: return "Summer"
    elif month in [9, 10, 11]: return "Autumn"
    return "Unknown"

class OpenMeteoClient(BaseHTTPClient):
    def __init__(self):
        super().__init__(timeout=15.0)

    async def _fetch_historical(self, lat: float, lon: float, start: str, end: str) -> dict:
        url = "https://historical-forecast-api.open-meteo.com/v1/archive"
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start,
            "end_date": end,
            "hourly": "temperature_2m,relative_humidity_2m,precipitation,weathercode",
            "timezone": "Africa/Nairobi"
        }
        return await self.get(url, params=params)

    async def _fetch_forecast(self, lat: float, lon: float, days: int) -> dict:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "forecast_days": days,
            "hourly": "temperature_2m,relative_humidity_2m,precipitation,weathercode",
            "timezone": "Africa/Nairobi"
        }
        return await self.get(url, params=params)

    async def get_weather_summary(self, lat: float, lon: float) -> WeatherSummary:
        today = datetime.now().date()
        start_past = str(today - timedelta(days=7))
        end_past = str(today - timedelta(days=1))
        future_days = 7

        # Fetch concurrently
        past_data, future_data = await asyncio.gather(
            self._fetch_historical(lat, lon, start_past, end_past),
            self._fetch_forecast(lat, lon, future_days),
            return_exceptions=True
        )

        df_past = pd.DataFrame()
        if not isinstance(past_data, Exception) and "hourly" in past_data:
            df_past = pd.DataFrame({
                "datetime": past_data["hourly"]["time"],
                "temperature (°C)": past_data["hourly"]["temperature_2m"],
                "humidity (%)": past_data["hourly"]["relative_humidity_2m"],
                "precipitation (mm)": past_data["hourly"]["precipitation"],
                "weather_code": past_data["hourly"]["weathercode"],
            })

        df_future = pd.DataFrame()
        if not isinstance(future_data, Exception) and "hourly" in future_data:
            df_future = pd.DataFrame({
                "datetime": future_data["hourly"]["time"],
                "temperature (°C)": future_data["hourly"]["temperature_2m"],
                "humidity (%)": future_data["hourly"]["relative_humidity_2m"],
                "precipitation (mm)": future_data["hourly"]["precipitation"],
                "weather_code": future_data["hourly"]["weathercode"],
            })

        # Combine
        if df_past.empty and df_future.empty:
            raise ValueError("Failed to fetch both historical and forecasted weather data.")
            
        df_all = pd.concat([df_past, df_future], ignore_index=True)
        df_all['datetime'] = pd.to_datetime(df_all['datetime'])
        df_all['weather_summary'] = df_all['weather_code'].map(WEATHER_CODES)
        
        df_all["month"] = df_all["datetime"].dt.month
        df_all["Season_et"] = df_all["month"].apply(get_season_et)
        df_all["Season_en"] = df_all["month"].apply(get_season_en)
        df_all["date"] = df_all["datetime"].dt.date

        start_date = df_all["date"].min()
        end_date = df_all["date"].max()

        daily_avg = df_all.groupby("date").agg({
            "temperature (°C)": "mean",
            "humidity (%)": "mean",
            "precipitation (mm)": "sum"
        }).reset_index()

        avg_temp = round(daily_avg["temperature (°C)"].mean(), 1)
        avg_humidity = round(daily_avg["humidity (%)"].mean(), 1)
        total_rain = round(daily_avg["precipitation (mm)"].sum(), 1)
        rainy_days = (daily_avg["precipitation (mm)"] > 1.0).sum()

        today_row = df_all[df_all["datetime"].dt.date == today]
        season_et = today_row["Season_et"].iloc[0] if not today_row.empty else "Unknown"
        season_en = today_row["Season_en"].iloc[0] if not today_row.empty else "Unknown"

        today_data = df_all[df_all["date"] == today]
        if not today_data.empty:
            today_temp = round(today_data["temperature (°C)"].mean(), 1)
            today_humidity = round(today_data["humidity (%)"].mean(), 1)
            today_precip = round(today_data["precipitation (mm)"].sum(), 1)
        else:
            today_temp = today_humidity = today_precip = "N/A"

        return WeatherSummary(
            start_date=str(start_date),
            today_date=str(today),
            end_date=str(end_date),
            season_et=season_et,
            season_en=season_en,
            avg_temperature=f"{avg_temp} °C",
            avg_humidity=f"{avg_humidity}%",
            total_precipitation=f"{total_rain} mm",
            rainy_days=int(rainy_days),
            today_weather={
                "temperature": f"{today_temp} °C",
                "humidity": f"{today_humidity}%",
                "precipitation": f"{today_precip} mm"
            }
        )

weather_client = OpenMeteoClient()
