import google.generativeai as genai
import asyncio
from datetime import datetime
from app.core.config import settings

# Load Gemini
genai.configure(api_key=settings.GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-3.1-flash-lite")

def generate_soil_summary_with_gemini(soil_data: str, weather_summary: str, location_data: str, elevation_data: str) -> str:
    """
    Given LLM-ready environmental data strings and an initialized Gemini model,
    generate a human-readable agricultural summary.
    """

    # Build the prompt
    prompt = f"""
    You are an expert agricultural advisor that helps farmers and investors understand soil
    and weather conditions in Africa.

    Below is the environmental data for a specific location. The data is provided in JSON/structured format.

    ## Location Information
    {location_data}

    ## Elevation
    {elevation_data} meters

    ## Weather Summary
    {weather_summary}

    ## Soil Data (High-Resolution ISDA Africa Data)
    {soil_data}

    ## Instructions for Your Response

    Using the above soil, weather, location, and elevation data:
    1. Start by mentioning the distance and direction of the input coordinate from the nearest city and the region it is in. Use one paragraph for this. 
    2. Say something informative about the city found from the location. If it has unnamed road or unknown location to get valuable info, just describe the regional state or the district it is in. Describe this part well in one paragraph.
    3. Describe the soil texture and fertility in simple terms based on the ISDA properties (e.g., Nitrogen, pH, Texture Class). Mention a few advantages and disadvantages of this soil. Use one paragraph to describe the soil and another to mention the advantages and disadvantages.
    4. Comment on how the current season, weather conditions, and elevation of the city affect crop growth using one paragraph.
    5. Recommend one or more crops suitable (arrange and rank them based on suitability to the soil) for this location considering the season it is in and the coming seasons in one paragraph. 
    6. Suggest fertilizers or soil improvements based on the nutrient levels provided in one paragraph.
    7. Add any water or irrigation advice if relevant in one paragraph.
    8. **Bolden important points from each paragraph and use bullet points for clarity.**
    9. Always start each paragraph with these exact titles:
        1. Location  
        2. City or Region Information 
        3. Soil Type and Fertility 
        4. Soil Advantages and Disadvantages  
        5. Seasonal Impacts on Crop Growth 
        6. Suitable Crop Recommendations
        7. Fertilizer and Soil Improvement Recommendations
        8. Water and Irrigation Advice

    Use clear, friendly, and practical language. Do not output raw JSON, just the readable report.
    """

    # Get Gemini response
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating AI summary: {str(e)}"
