from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.deps import Scope, get_scope
from src.agents.task_agent.service import TaskService
from src.core.schemas.tasks import TaskCreateRequest, TaskUpdateRequest
from src.core.utils.responses import ok

router = APIRouter(
    prefix="/api/tasks",
    tags=["Tasks"],
)


@router.get("")
def list_tasks(
    status: Optional[str] = Query(None),
    sort: str = Query("created_at"),
    order: str = Query("desc"),
    limit: Optional[int] = Query(None, ge=1, le=200),
    offset: int = Query(0, ge=0),
    scope: Scope = Depends(get_scope),
):
    result = TaskService.list(
        scope.user_id,
        scope.workspace_id,
        status=status,
        sort=sort,
        order=order,
        limit=limit,
        offset=offset,
    )
    return ok(result)


@router.post("")
def create_task(
    payload: TaskCreateRequest,
    scope: Scope = Depends(get_scope),
):
    result = TaskService.create(
        scope.user_id,
        scope.workspace_id,
        payload.title,
        payload.description,
        payload.due_date,
    )
    return ok(result)


@router.patch("/{task_id}")
def update_task(
    task_id: int,
    payload: TaskUpdateRequest,
    scope: Scope = Depends(get_scope),
):
    params = {"task_id": task_id, **payload.model_dump(exclude_none=True)}
    result = TaskService.update(scope.user_id, scope.workspace_id, params)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("message"))
    return ok(result)


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    scope: Scope = Depends(get_scope),
):
    result = TaskService.delete(
        scope.user_id,
        scope.workspace_id,
        {"task_id": task_id},
    )
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("message"))
    return ok(result)
