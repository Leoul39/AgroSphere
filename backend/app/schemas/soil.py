from pydantic import BaseModel
from typing import List, Optional, Union

class SoilPropertyBase(BaseModel):
    code: str
    name: str
    mapped_units: str
    target_units: str
    depth_label: str
    mean: Union[float, str]

# Responses
class SoilPropertyResponse(BaseModel):
    properties: List[SoilPropertyBase]
