from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.schemas.chat import ChatRequest
from src.core.db.database import get_db
from src.graph.workflow import graph
from src.auth.dependencies import get_current_user
from src.workspaces.resolver import resolve_workspace_id
from src.core.utils.responses import ok

router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)


@router.post("/")
def chat(
        payload: ChatRequest,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db),
):
    workspace_id = resolve_workspace_id(
        db,
        current_user.id,
        payload.workspace_id,
    )

    result = graph.invoke(
        {
            "user_id": current_user.id,
            "workspace_id": workspace_id,
            "message": payload.message,
            "plan": None,
            "steps": [],
            "results": [],
            "response": "",
        }
    )
    return ok(result)
