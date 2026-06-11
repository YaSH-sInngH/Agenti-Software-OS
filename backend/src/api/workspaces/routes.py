from typing import List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
)
from fastapi.responses import Response
from sqlalchemy.orm import Session

from src.core.db.database import get_db
from src.core.schemas.workspace import (
    WorkspaceCreateRequest,
    WorkspaceUpdateRequest,
)
from src.auth.dependencies import get_current_user
from src.workspaces.service import WorkspaceService, serialize_workspace
from src.workspaces import files as fs
from src.agents.indexer_agent.service import WorkspaceIndexerService
from src.core.utils.responses import ok

router = APIRouter(
    prefix="/api/workspaces",
    tags=["Workspaces"],
)


def get_owned_workspace(
    workspace_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    workspace = WorkspaceService.get(db, current_user.id, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace


@router.get("")
def list_workspaces(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    workspaces = WorkspaceService.list(db, current_user.id)
    return ok([serialize_workspace(w) for w in workspaces])


@router.post("")
def create_workspace(
    payload: WorkspaceCreateRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    workspace = WorkspaceService.create(db, current_user.id, payload.name)
    return ok(serialize_workspace(workspace))


@router.patch("/{workspace_id}")
def rename_workspace(
    payload: WorkspaceUpdateRequest,
    workspace=Depends(get_owned_workspace),
    db: Session = Depends(get_db),
):
    workspace = WorkspaceService.rename(db, workspace, payload.name)
    return ok(serialize_workspace(workspace))


@router.delete("/{workspace_id}")
def delete_workspace(
    workspace=Depends(get_owned_workspace),
    db: Session = Depends(get_db),
):
    WorkspaceService.delete(db, workspace)
    return ok({"message": "Workspace deleted"})


# ---- Files ----

@router.get("/{workspace_id}/files")
def list_files(
    workspace=Depends(get_owned_workspace),
):
    return ok(fs.build_tree(workspace.id))


@router.get("/{workspace_id}/files/{file_path:path}")
def read_file(
    file_path: str,
    workspace=Depends(get_owned_workspace),
):
    try:
        content = fs.read_file_bytes(workspace.id, file_path)
    except fs.UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))

    try:
        text = content.decode("utf-8")
        return ok({"path": file_path, "content": text, "encoding": "utf-8"})
    except UnicodeDecodeError:
        return ok({
            "path": file_path,
            "content": None,
            "encoding": "binary",
            "message": "Binary file; use the download endpoint",
        })


@router.delete("/{workspace_id}/files/{file_path:path}")
def delete_file(
    file_path: str,
    workspace=Depends(get_owned_workspace),
):
    try:
        removed = fs.delete_path(workspace.id, file_path)
    except fs.UploadError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not removed:
        raise HTTPException(status_code=404, detail="Path not found")

    return ok({"message": "Deleted", "path": file_path})


@router.get("/{workspace_id}/download/{file_path:path}")
def download_file(
    file_path: str,
    workspace=Depends(get_owned_workspace),
):
    try:
        content = fs.read_file_bytes(workspace.id, file_path)
    except fs.UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))

    filename = file_path.rsplit("/", 1)[-1]
    return Response(
        content=content,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        },
    )


@router.post("/{workspace_id}/upload")
async def upload_files(
    files: List[UploadFile] = File(...),
    paths: List[str] = Form(default=[]),
    auto_index: bool = Form(default=True),
    workspace=Depends(get_owned_workspace),
    current_user=Depends(get_current_user),
):
    # Supports plain files, folder uploads (relative paths via `paths`),
    # and .zip imports (extracted in place).
    saved = []
    errors = []

    for i, upload in enumerate(files):
        # Prefer an explicit relative path (folder import), else the filename.
        rel = paths[i] if i < len(paths) and paths[i] else upload.filename
        content = await upload.read()

        try:
            if rel.lower().endswith(".zip"):
                prefix = rel[:-4].rsplit("/", 1)[0] if "/" in rel else ""
                saved.extend(fs.extract_zip(workspace.id, content, prefix))
            else:
                saved.append(fs.save_upload(workspace.id, rel, content))
        except fs.UploadError as e:
            errors.append({"file": rel, "error": str(e)})

    indexing = None
    if auto_index and saved:
        indexing = WorkspaceIndexerService.index_workspace_background(
            current_user.id,
            workspace.id,
        )

    return ok({
        "saved": saved,
        "errors": errors,
        "indexing": indexing,
    })
