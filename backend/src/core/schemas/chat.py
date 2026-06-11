from typing import Optional
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    workspace_id: Optional[int] = None
