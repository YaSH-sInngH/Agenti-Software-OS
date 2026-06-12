import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from src.core.db.database import get_db
from src.auth.dependencies import get_current_user
from src.workspaces.resolver import resolve_workspace_id
from src.graph.context import WorkspaceContext
from src.graph.nodes import planner_node, router_nodes, response_node, execute_step
from src.agents.response_agent.executor import response_agent_executor
from src.runs.service import RunService
from src.core.schemas.orchestration import PlanRequest, RunRequest
from src.core.utils.responses import ok


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"

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

    run = RunService.create(
        current_user.id,
        workspace_id,
        payload.message or "",
        payload.steps,
        state["results"],
        state["response"],
    )

    return ok({
        "workspace_id": workspace_id,
        "run_id": run["id"],
        "results": state["results"],
        "response": state["response"],
    })


@router.post("/run/stream")
def run_stream(
    payload: RunRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Stream execution of approved/edited steps, emitting per-step events so the
    # approve-then-run path animates live (same event shape as /api/chat/stream).
    workspace_id = resolve_workspace_id(db, current_user.id, payload.workspace_id)
    user_id = current_user.id
    steps = payload.steps
    message = payload.message or ""

    def event_stream():
        context = WorkspaceContext(user_id=user_id, workspace_id=workspace_id)

        yield _sse("plan_ready", {"workspace_id": workspace_id, "steps": steps})

        results = []
        for i, step in enumerate(steps):
            yield _sse("step_started", {
                "index": i,
                "agent": step.get("agent"),
                "action": step.get("action"),
            })
            record = execute_step(step, results, context)
            results.append(record)
            yield _sse("step_done", {
                "index": i,
                "agent": record["agent"],
                "action": record["action"],
                "result": record["result"],
            })

        response = response_agent_executor(message, results)
        run = RunService.create(
            user_id, workspace_id, message, steps, results, response
        )

        yield _sse("final_response", {
            "run_id": run["id"],
            "response": response,
            "results": results,
        })
        yield _sse("done", {"run_id": run["id"]})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
