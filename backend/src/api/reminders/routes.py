from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.deps import Scope, get_scope
from src.agents.reminder_agent.service import ReminderService
from src.core.schemas.reminders import ReminderCreateRequest
from src.core.utils.responses import ok

router = APIRouter(
    prefix="/api/reminders",
    tags=["Reminders"],
)


@router.get("")
def list_reminders(
    status: Optional[str] = Query(None),
    sort: str = Query("remind_at"),
    order: str = Query("asc"),
    limit: Optional[int] = Query(None, ge=1, le=200),
    offset: int = Query(0, ge=0),
    scope: Scope = Depends(get_scope),
):
    result = ReminderService.list(
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
def create_reminder(
    payload: ReminderCreateRequest,
    scope: Scope = Depends(get_scope),
):
    result = ReminderService.create(
        scope.user_id,
        scope.workspace_id,
        payload.message,
        payload.remind_at,
    )
    return ok(result)


@router.get("/due")
def due_reminders(
    scope: Scope = Depends(get_scope),
):
    return ok(ReminderService.due(scope.user_id, scope.workspace_id))


@router.get("/daily-summary")
def daily_summary(
    scope: Scope = Depends(get_scope),
):
    return ok(ReminderService.daily_summary(scope.user_id, scope.workspace_id))


@router.delete("/{reminder_id}")
def delete_reminder(
    reminder_id: int,
    scope: Scope = Depends(get_scope),
):
    result = ReminderService.delete(
        scope.user_id,
        scope.workspace_id,
        {"reminder_id": reminder_id},
    )
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("message"))
    return ok(result)
