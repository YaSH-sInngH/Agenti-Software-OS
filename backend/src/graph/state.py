from typing import TypedDict, Optional, Dict, Any

class AgentState(TypedDict):
    user_id: int
    message: str
    plan: Optional[Dict[str, Any]]
    response: str