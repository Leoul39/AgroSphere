from pydantic import BaseModel
from typing import List, Optional

class SoilPropertyBase(BaseModel):
    code: str
    name: str
    mapped_units: str
    target_units: str
    depth_label: str
    mean: float

class SoilProbabilityBase(BaseModel):
    soil_type: str
    probability_percent: str

# Responses
class SoilPropertyResponse(BaseModel):
    properties: List[SoilPropertyBase]

class SoilProbabilityResponse(BaseModel):
    probabilities: List[SoilProbabilityBase]
