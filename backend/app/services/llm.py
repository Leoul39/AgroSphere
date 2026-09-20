import google.generativeai as genai
import asyncio
import json
from datetime import datetime
from app.core.config import settings
from app.schemas.report import AgriculturalReport

# Load Gemini
genai.configure(api_key=settings.GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-3.1-flash-lite")

def generate_soil_summary_with_gemini(soil_data: str, weather_summary: str, location_data: str, elevation_data: str, is_farmable: bool, unfarmable_reason: str) -> dict:
    """
    Given LLM-ready environmental data strings and an initialized Gemini model,
    generate a highly structured AgriculturalReport JSON.
    """

    # Build the prompt
    prompt = f"""
    You are an expert agricultural AI engine that analyzes soil and weather conditions in Africa.
    Your output MUST strictly conform to the requested JSON schema. Do NOT output markdown text.

    ## STRICT ENFORCEMENT RULES
    IS_FARMABLE = {is_farmable}
    UNFARMABLE_REASON = "{unfarmable_reason}"

    1. You MUST set the JSON field `is_farmable` to exactly {is_farmable}. Do not second-guess this.
    2. If IS_FARMABLE is False:
       - You MUST set `unfarmable_reason` to exactly: "{unfarmable_reason}"
       - You MUST set `recommended_crops`, `soil_amendments`, and `risk_factors` to empty arrays `[]`.
       - DO NOT recommend crops or fertilizers under any circumstances.
    3. If IS_FARMABLE is True:
       - Set `unfarmable_reason` to null.
       - Recommend suitable crops and fertilizers based on the data.

    ## Location Information
    {location_data}

    ## Elevation
    {elevation_data} meters

    ## Weather Summary
    {weather_summary}

    ## Soil Data (High-Resolution ISDA Africa Data)
    {soil_data}

    ## Instructions
    Analyze the above data comprehensively. Provide detailed summaries for climate and soil health. 
    If `soil_data` is empty, missing, or contains an Exception, do NOT hallucinate an API error or authentication failure. Simply state that detailed soil data is not available for this specific coordinate.
    If the land IS farmable, recommend the best suitable crops and actionable soil amendments (fertilizers) based on the nutrient levels.
    Identify any risk factors like waterlogging, extreme cold/heat, or poor drainage.
    """

    print("================ PROMPT SENT TO GEMINI ================")
    print(f"is_farmable flag passed to function: {is_farmable}")
    print(f"unfarmable_reason passed to function: {unfarmable_reason}")
    print(prompt)
    print("======================================================")

    # Get Gemini response
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=AgriculturalReport,
                temperature=0.2
            )
        )
        return json.loads(response.text)
    except Exception as e:
        return {"error": f"Failed to generate AI summary: {str(e)}"}
