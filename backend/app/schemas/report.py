from pydantic import BaseModel, Field
from typing import List, Optional

class CropRecommendation(BaseModel):
    crop_name: str = Field(description="The name of the recommended crop.")
    suitability_score: int = Field(description="A score from 0 to 100 indicating how suitable the crop is for the location.")
    rationale: str = Field(description="A detailed explanation of why this crop is recommended based on the soil and climate.")
    estimated_growing_days: Optional[int] = Field(description="Estimated days to maturity in this climate.")

class SoilAmendment(BaseModel):
    amendment_type: str = Field(description="Type of fertilizer or soil amendment (e.g., Urea, Compost, Lime).")
    application_reason: str = Field(description="Why this amendment is needed based on the soil data.")
    recommended_timing: str = Field(description="When to apply the amendment (e.g., At planting, Top dressing).")

class RiskFactor(BaseModel):
    risk_type: str = Field(description="The type of risk (e.g., Frost, Waterlogging, Acidity, Drought).")
    description: str = Field(description="Details about the risk based on the data.")
    mitigation_strategy: str = Field(description="How the farmer can mitigate this risk.")

class AgriculturalReport(BaseModel):
    is_farmable: bool = Field(description="True if the location is suitable for farming, False if it is urban, concrete, or otherwise unfarmable.")
    unfarmable_reason: Optional[str] = Field(description="If not farmable, clearly explain why to the user (e.g., Urban area, Highway).")
    
    general_location_summary: str = Field(description="A brief description of the geographic region, district, and nearest city based on OpenStreetMap data.")
    coordinate_specific_summary: str = Field(description="A precise description of the exact terrain and landscape at the specific coordinates, heavily prioritizing the crop_cover_2019 satellite percentage.")
    climate_summary: str = Field(description="A comprehensive summary of the current and expected weather patterns, seasons, and elevation impact.")
    soil_health_summary: str = Field(description="A comprehensive summary of the soil composition, texture, and fertility based on ISDA properties.")
    
    recommended_crops: List[CropRecommendation] = Field(description="Ranked list of highly suitable crops.")
    soil_amendments: List[SoilAmendment] = Field(description="Actionable fertilizer and amendment recommendations.")
    risk_factors: List[RiskFactor] = Field(description="Identified risks from extreme weather or poor soil properties.")
    irrigation_advice: str = Field(description="Specific advice on water management and irrigation.")
