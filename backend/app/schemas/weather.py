from pydantic import BaseModel

class WeatherSummary(BaseModel):
    start_date: str
    today_date: str
    end_date: str
    season_et: str
    season_en: str
    avg_temperature: str
    avg_humidity: str
    total_precipitation: str
    rainy_days: int
    today_weather: dict
