from typing import TypedDict, Optional, Dict, Any, List

class AgentState(TypedDict):
    user_id: int
    workspace_id: int
    message: str
    plan: Optional[Dict[str, Any]]
    steps: List[Dict[str, Any]]
    results: List[Dict[str, Any]]
    response: str
