from pydantic import BaseModel
from typing import List, Dict, Optional, Union

class Technology(BaseModel):
    name: str
    category: str
    version: Optional[str] = None
    description: Optional[str] = None

class TechStackRecommendationRequest(BaseModel):
    description: str
    requirements: List[str]
    constraints: Dict[str, Union[str, List[str]]] = {}

class TechStackRecommendationResponse(BaseModel):
    primary_tech_stack: List[Technology]
    alternatives: Dict[str, List[Technology]]
    explanation: str
    confidence_level: float
    similar_projects: List[Dict] = [] 