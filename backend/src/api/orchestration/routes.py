from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.db.database import get_db
from src.auth.dependencies import get_current_user
from src.workspaces.resolver import resolve_workspace_id
from src.graph.nodes import planner_node, router_nodes, response_node
from src.core.schemas.orchestration import PlanRequest, RunRequest
from src.core.utils.responses import ok

router = APIRouter(
    prefix="/api",
    tags=["Orchestration"],
)


def _empty_state(user_id, workspace_id, message, steps):
    return {
        "user_id": user_id,
        "workspace_id": workspace_id,
        "message": message,
        "plan": None,
        "steps": steps,
        "results": [],
        "response": "",
    }


@router.post("/plan")
def plan(
    payload: PlanRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Planning only — no execution. Returns the steps for preview / approval.
    workspace_id = resolve_workspace_id(db, current_user.id, payload.workspace_id)

    state = _empty_state(
        current_user.id,
        workspace_id,
        payload.message,
        [],
    )
    state = planner_node(state)

    return ok({
        "workspace_id": workspace_id,
        "plan": state["plan"],
        "steps": state["steps"],
    })


@router.post("/run")
def run(
    payload: RunRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Execute approved/edited steps (with orchestration) + friendly response.
    workspace_id = resolve_workspace_id(db, current_user.id, payload.workspace_id)

    state = _empty_state(
        current_user.id,
        workspace_id,
        payload.message or "",
        payload.steps,
    )
    state = router_nodes(state)
    state = response_node(state)

    return ok({
        "workspace_id": workspace_id,
        "results": state["results"],
        "response": state["response"],
    })
