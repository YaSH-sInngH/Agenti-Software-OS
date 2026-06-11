import os

from fastapi import APIRouter, Depends, HTTPException

try:
    from cohere.errors import TooManyRequestsError
except Exception:  # pragma: no cover - defensive import
    TooManyRequestsError = None

from src.api.deps import Scope, get_scope
from src.core.utils.workspace import resolve_workspace_file
from src.agents.knowledge_agent.service import KnowledgeService
from src.agents.indexer_agent.service import WorkspaceIndexerService
from src.core.schemas.knowledge import (
    KnowledgeSearchRequest,
    KnowledgeIndexRequest,
)
from src.core.utils.responses import ok

router = APIRouter(
    prefix="/api/knowledge",
    tags=["Knowledge"],
)


@router.get("/status")
def knowledge_status(
    scope: Scope = Depends(get_scope),
):
    # What's indexed in this workspace.
    return ok(
        WorkspaceIndexerService.status(scope.user_id, scope.workspace_id)
    )


@router.post("/search")
def knowledge_search(
    payload: KnowledgeSearchRequest,
    scope: Scope = Depends(get_scope),
):
    return ok(
        KnowledgeService.search_workspace(
            payload.query,
            scope.workspace_id,
            top_k=payload.top_k,
        )
    )


@router.post("/index")
def knowledge_index(
    payload: KnowledgeIndexRequest,
    scope: Scope = Depends(get_scope),
):
    try:
        path = resolve_workspace_file(scope.workspace_id, payload.file_path)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid file path")

    if not os.path.isfile(path):
        raise HTTPException(
            status_code=404,
            detail=f"File not found in workspace: {payload.file_path}",
        )

    try:
        result = KnowledgeService.index_document(
            payload.file_path,
            scope.workspace_id,
        )
    except ValueError as e:
        # Unsupported file type (e.g. not pdf/docx/txt).
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        if TooManyRequestsError and isinstance(e, TooManyRequestsError):
            raise HTTPException(
                status_code=429,
                detail=(
                    "Embedding provider rate limit hit (Cohere trial key: "
                    "40 calls/min). Wait a minute and retry."
                ),
            )
        raise

    # Record it so /knowledge/status reflects this document.
    WorkspaceIndexerService.record_file(
        scope.user_id,
        scope.workspace_id,
        payload.file_path,
    )

    return ok(result)
