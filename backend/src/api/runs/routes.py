from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.deps import Scope, get_scope
from src.runs.service import RunService
from src.core.utils.responses import ok

router = APIRouter(
    prefix="/api/runs",
    tags=["Runs"],
)


@router.get("")
def list_runs(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    scope: Scope = Depends(get_scope),
):
    return ok(
        RunService.list(
            scope.user_id,
            scope.workspace_id,
            limit=limit,
            offset=offset,
        )
    )


@router.get("/{run_id}")
def get_run(
    run_id: int,
    scope: Scope = Depends(get_scope),
):
    run = RunService.get(scope.user_id, scope.workspace_id, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return ok(run)
