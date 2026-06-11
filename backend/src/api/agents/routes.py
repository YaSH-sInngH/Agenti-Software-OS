from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.db.database import get_db
from src.auth.dependencies import get_current_user
from src.workspaces.resolver import resolve_workspace_id
from src.agents.registry import AGENT_REGISTRY
from src.agents.manifest import get_manifest, get_agent
from src.graph.context import WorkspaceContext
from src.core.schemas.orchestration import AgentRunRequest
from src.core.utils.responses import ok

router = APIRouter(
    prefix="/api/agents",
    tags=["Agents"],
)


@router.get("")
def list_agents(
    current_user=Depends(get_current_user),
):
    return ok(get_manifest())


@router.post("/{name}/run")
def run_agent(
    name: str,
    payload: AgentRunRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Direct executor call — no LLM planning. Powers dashboard buttons.
    executor = AGENT_REGISTRY.get(name)
    if not executor:
        raise HTTPException(status_code=404, detail=f"Unknown agent: {name}")

    meta = get_agent(name)
    if meta is not None:
        valid_actions = {a["name"] for a in meta["actions"]}
        if payload.action not in valid_actions:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown action '{payload.action}' for {name}",
            )

    workspace_id = resolve_workspace_id(db, current_user.id, payload.workspace_id)

    context = WorkspaceContext(
        user_id=current_user.id,
        workspace_id=workspace_id,
    )

    try:
        result = executor(
            {"action": payload.action, "parameters": payload.parameters},
            context,
        )
    except Exception as e:
        result = {
            "success": False,
            "message": f"{type(e).__name__}: {e}",
        }

    return ok({
        "agent": name,
        "action": payload.action,
        "workspace_id": workspace_id,
        "result": result,
    })
