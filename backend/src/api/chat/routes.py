import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from src.core.schemas.chat import ChatRequest
from src.core.db.database import get_db
from src.graph.workflow import graph
from src.graph.context import WorkspaceContext
from src.graph.nodes import planner_node, execute_step
from src.agents.response_agent.executor import response_agent_executor
from src.auth.dependencies import get_current_user
from src.workspaces.resolver import resolve_workspace_id
from src.runs.service import RunService
from src.core.utils.responses import ok

router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"


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

    run = RunService.create(
        current_user.id,
        workspace_id,
        payload.message,
        result.get("steps"),
        result.get("results"),
        result.get("response"),
    )
    result["run_id"] = run["id"]

    return ok(result)


@router.post("/stream")
def chat_stream(
        payload: ChatRequest,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db),
):
    # Server-Sent Events: plan_ready -> step_started/step_done (per step)
    # -> final_response -> done. Powers the live step graph.
    workspace_id = resolve_workspace_id(
        db,
        current_user.id,
        payload.workspace_id,
    )
    user_id = current_user.id
    message = payload.message

    def event_stream():
        context = WorkspaceContext(user_id=user_id, workspace_id=workspace_id)

        # 1. Plan
        state = planner_node({
            "user_id": user_id,
            "workspace_id": workspace_id,
            "message": message,
            "plan": None,
            "steps": [],
            "results": [],
            "response": "",
        })
        steps = state["steps"]

        yield _sse("plan_ready", {
            "workspace_id": workspace_id,
            "plan": state["plan"],
            "steps": steps,
        })

        # 2. Execute step by step
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

        # 3. Friendly response
        response = response_agent_executor(message, results)

        # 4. Persist to run history
        run = RunService.create(
            user_id,
            workspace_id,
            message,
            steps,
            results,
            response,
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
