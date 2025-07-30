import google.generativeai as genai
from isda import fetch_isda_soil_property
from weather import fetch_weather_open, summarize_weather_dataframe
from location import reverse_geocode
from elevation import get_elevation
from dotenv import load_dotenv
import os
import asyncio
from datetime import datetime

load_dotenv()

# Load Gemini
api_key=os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

def generate_soil_summary_with_gemini(soil_data, weather_summary,location_data,elevation_data) -> str:
    """
    Given LLM-ready soil data and an initialized Gemini model,
    generate a human-readable agricultural summary.
    """

    # Extract basic soil inputs
    lat = soil_data["coordinates"]["lat"]
    lon = soil_data["coordinates"]["lon"]
    depth = soil_data["depth"]
    properties = soil_data["properties"]

    # Weather summary values extraction
    start = weather_summary["start_date"]
    end = weather_summary["end_date"]
    today = weather_summary["today_date"]
    season_et = weather_summary["season_et"]
    season_en = weather_summary["season_en"]
    avg_temp = weather_summary["avg_temperature"]
    avg_humidity = weather_summary["avg_humidity"]
    total_precip = weather_summary["total_precipitation"]
    rainy_days = weather_summary["rainy_days"]
    today_temp = weather_summary["today_weather"]["temperature"]
    today_humidity = weather_summary["today_weather"]["humidity"]
    today_precip = weather_summary["today_weather"]["precipitation"]

    # Location data extraction
    bounds_city = location_data['bounds_of_city']
    location_info = location_data['locational_info']
    city = location_data['formatted_city']
    center = location_data['center_of_city']
    distance_from_center = location_data['distance_from_city'] 

    # Build the prompt
    prompt = f"""

    You are an agricultural advisor that can help both farmers and investors understand soil
    and weather conditions in Ethiopia.

    ## Soil Location
    - Coordinates: ({lat}, {lon})
    - Soil Sampling Depth: {depth['value']} {depth['unit']}

    ## Weather Summary
    - Date Range: {start} to {end}
    - Today's Date: {today}
    - Ethiopian Season: {season_et}
    - Global Season: {season_en}
    - Avg Temperature: {avg_temp}
    - Avg Humidity: {avg_humidity}
    - Total Rainfall: {total_precip} over {rainy_days} days\

    ### Today's Conditions
    - Temperature: {today_temp}
    - Humidity: {today_humidity}
    - Rainfall: {today_precip}

    ## Location Information
    - Geographical bounds of the closest city: {bounds_city}
    - Location details(you'll probably get the city or the state district from this): {location_info}
    - City(if unknown look for it in the location info): {city}
    - Center of the mentioned city: {center}
    - Distance from the center of the city: {distance_from_center} km

    ### Elevation
    - Elevation of the coordinate {elevation_data}

    ## Soil Data
    Each property includes a predicted value and its 90% confidence interval.
    """
        # Append each soil property
    for prop, details in properties.items():
            unit = details.get("unit", "")
            value = details.get("predicted_value", "N/A")
            bounds = details.get("interval_for_value_90pct", {})
            lower = bounds.get("lower_bound", "N/A")
            upper = bounds.get("upper_bound", "N/A")

            prompt += f"\n- {prop.replace('_', ' ').title()}: {value} {unit or ''} (90% CI: {lower}–{upper})"


    # Final instructions to Gemini
    prompt += """
    
    ## Instructions for Your Response

    Using the above soil, weather, location and elevation data:
    1. Start by mentioning the distance and direction of the input coordinate from the nearest city and the region it is in. Use one paragraph for this. 
    2. Say something informative about the city found from the location. If it has unnamed road or unknown location to get valuable info, just describe the regional state or the district it is in. Describe this part well in one paragraph.
    3. Describe the soil type and fertility of the soil in simple terms. Mention few advantages and disadvantages of the soil. Use one paragraph to describe the soil and another to mention the advantages and disadvantages.
    4. Comment on how the current season, weather conditions and elevation of the city affect crop growth using one paragraph.
    5. Recommend one or more crops suitable(arrange and rank them based on suitability to the soil) for this location considering the season it is in and the coming seasons in one paragraph. 
    6. Suggest fertilizers or soil improvements based on nutrients in one paragraph.
    7. Add any water or irrigation advice if relevant in one paragraph.
    8. **Bolden important points from each paragraph and use bullet points for clarity as found in markdown language.**
    9. Always start each paragraph with these titles:   1. Location  
                                                        2. City or Region Information 
                                                        3. Soil Type and Fertility 
                                                        4. Soil Advantages and Disadvantages  
                                                        5. Seasonal Impacts on Crop Growth 
                                                        6. Suitable Crop Recommendations
                                                        7. Fertilizer and Soil Improvement Recommendations
                                                        8. Water and Irrigation Advice

    Use clear and friendly language.
    """

    # Get Gemini response
    response = model.generate_content(prompt)
    return response.text
