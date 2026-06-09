from pydantic import BaseModel
from typing import Dict, Any

class PlannerOutput(BaseModel):
    agent: str
    action: str
    parameters: Dict[str, Any]