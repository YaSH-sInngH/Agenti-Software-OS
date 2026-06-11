from typing import Optional
from pydantic import BaseModel


class ReminderCreateRequest(BaseModel):
    message: str
    remind_at: Optional[str] = None
