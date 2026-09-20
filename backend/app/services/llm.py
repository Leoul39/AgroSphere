import google.generativeai as genai
import asyncio
import json
import logging
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.core.config import settings
from app.schemas.report import AgriculturalReport
from pydantic import ValidationError
from google.api_core.exceptions import GoogleAPIError

logger = logging.getLogger(__name__)

# Load Gemini Configuration
genai.configure(api_key=settings.GOOGLE_API_KEY)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((GoogleAPIError, ValidationError)),
    reraise=True
)
async def _generate_with_retry(prompt: str, generation_config: genai.GenerationConfig, system_instruction: str) -> AgriculturalReport:
    """Internal function to call Gemini asynchronously with retries and strict Pydantic validation."""
    
    # Instantiate the model with the system_instruction bound to it
    local_model = genai.GenerativeModel(
        "gemini-3.1-flash-lite",
        system_instruction=system_instruction
    )

    logger.info("Calling Gemini API asynchronously...")
    response = await local_model.generate_content_async(
        prompt,
        generation_config=generation_config
    )
    
    # Run the raw response back through our Pydantic schema for post-generation validation.
    # If Gemini hallucinated the schema or missed fields, this throws a ValidationError and triggers a retry.
    return AgriculturalReport.model_validate_json(response.text)

async def generate_soil_summary_with_gemini(soil_data: str, weather_summary: str, location_data: str, elevation_data: str, is_farmable: bool, unfarmable_reason: str) -> dict:
    """
    Given LLM-ready environmental data strings, generates a highly structured AgriculturalReport JSON.
    """

    # Build the System Instruction (Persona, Strict Rules, & Comprehensive instructions)
    system_instruction = f"""You are an expert agricultural AI engine that analyzes soil and weather conditions in Africa.
Your output MUST strictly conform to the requested JSON schema. Do NOT output markdown text.

## STRICT ENFORCEMENT RULES
IS_FARMABLE = {is_farmable}
UNFARMABLE_REASON = "{unfarmable_reason}"

1. You MUST set the JSON field `is_farmable` to exactly {is_farmable}. Do not second-guess this.
2. If IS_FARMABLE is False:
   - You MUST set `unfarmable_reason`, `soil_health_summary`, and `irrigation_advice` to exactly: "{unfarmable_reason}"
   - You MUST set `recommended_crops`, `soil_amendments`, and `risk_factors` to empty arrays `[]`.
   - DO NOT recommend crops or fertilizers under any circumstances.
3. If IS_FARMABLE is True:
   - Set `unfarmable_reason` to null.
   - Recommend suitable crops and fertilizers based on the data.

## COMPREHENSIVE SUMMARIES
If IS_FARMABLE is True, you MUST write highly detailed, comprehensive summaries (3-5 sentences each) for `climate_summary`, `general_location_summary`, `coordinate_specific_summary`, and `soil_health_summary`.

CRITICAL RULE FOR LOCATION:
- `general_location_summary`: Describe the broader region and district based on the OpenStreetMap location data.
- `coordinate_specific_summary`: Describe the EXACT terrain at the coordinate. You MUST prioritize the `crop_cover_2019` percentage from the soil data. If the historical crop cover is > 5%, you MUST describe it as an active or historical agricultural field. DO NOT hallucinate forests, cities, or lakes based on the general OpenStreetMap district name. The OpenStreetMap name is just a district boundary, while the crop_cover_2019 is exact satellite ground-truth.

If `soil_data` is empty, missing, or contains an Exception, do NOT hallucinate an API error. Simply state that detailed soil data is not available."""

    # Build the User Prompt (Just the data)
    prompt = f"""## Location Information
{location_data}

## Elevation
{elevation_data} meters

## Weather Summary
{weather_summary}

## Soil Data (High-Resolution ISDA Africa Data)
{soil_data}

Analyze the above data comprehensively based on your system instructions."""

    generation_config = genai.GenerationConfig(
        response_mime_type="application/json",
        response_schema=AgriculturalReport,
        temperature=0.2
    )

    try:
        start_time = datetime.now()
        report = await _generate_with_retry(prompt, generation_config, system_instruction)
        logger.info(f"Successfully generated AI summary in {(datetime.now() - start_time).total_seconds():.2f}s")
        return report.model_dump()
    except Exception as e:
        logger.error(f"Failed to generate AI summary after retries: {str(e)}")
        return {"error": f"Failed to generate AI summary: {str(e)}"}
