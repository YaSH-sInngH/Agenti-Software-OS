from fastapi import APIRouter, Depends, Query

from src.api.deps import Scope, get_scope
from src.dashboard.service import DashboardService
from src.agents.knowledge_agent.service import KnowledgeService
from src.core.utils.responses import ok

router = APIRouter(
    prefix="/api",
    tags=["Dashboard"],
)


@router.get("/dashboard")
def dashboard(
    scope: Scope = Depends(get_scope),
):
    return ok(DashboardService.overview(scope.user_id, scope.workspace_id))


@router.get("/search")
def search(
    q: str = Query(..., min_length=1),
    scope: Scope = Depends(get_scope),
):
    db_results = DashboardService.search_db(scope.user_id, scope.workspace_id, q)

    # Documents come from the knowledge vector store.
    try:
        doc_result = KnowledgeService.search_workspace(
            q,
            scope.workspace_id,
            top_k=5,
        )
        documents = doc_result.get("results", [])
    except Exception:
        documents = []

    return ok({
        "query": q,
        "documents": documents,
        "tasks": db_results["tasks"],
        "memories": db_results["memories"],
    })
