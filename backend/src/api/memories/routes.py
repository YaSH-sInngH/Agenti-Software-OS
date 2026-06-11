from fastapi import APIRouter, Depends, HTTPException

from src.api.deps import Scope, get_scope
from src.agents.memory_agent.service import MemoryService
from src.core.utils.responses import ok

router = APIRouter(
    prefix="/api/memories",
    tags=["Memories"],
)


@router.get("")
def list_memories(
    scope: Scope = Depends(get_scope),
):
    return ok(MemoryService.list(scope.user_id, scope.workspace_id))


@router.delete("/{memory_id}")
def delete_memory(
    memory_id: int,
    scope: Scope = Depends(get_scope),
):
    result = MemoryService.delete(scope.user_id, scope.workspace_id, memory_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("message"))
    return ok(result)
