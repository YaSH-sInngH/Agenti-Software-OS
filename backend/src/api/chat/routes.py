from fastapi import APIRouter, Depends
from src.schemas.chat import ChatRequest
from src.graph.workflow import graph
from src.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)

@router.post("/")
def chat(
        payload: ChatRequest,
        current_user=Depends(get_current_user),
):
    result = graph.invoke(
        {
            "user_id": current_user.id,
            "message": payload.message,
            "plan": None,
            "result": {},
            "response": "",
        }
    )
    return result

