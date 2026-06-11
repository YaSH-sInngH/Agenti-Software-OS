from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class PlanRequest(BaseModel):
    message: str
    workspace_id: Optional[int] = None


class RunRequest(BaseModel):
    steps: List[Dict[str, Any]]
    message: Optional[str] = ""
    workspace_id: Optional[int] = None


class AgentRunRequest(BaseModel):
    action: str
    parameters: Dict[str, Any] = {}
    workspace_id: Optional[int] = None
