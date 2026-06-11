from fastapi import HTTPException

from src.workspaces.service import WorkspaceService


def resolve_workspace_id(db, user_id: int, workspace_id):
    # Validate an explicit workspace belongs to the user, or fall back to default.
    if workspace_id is not None:
        workspace = WorkspaceService.get(db, user_id, workspace_id)
        if not workspace:
            raise HTTPException(
                status_code=404,
                detail="Workspace not found",
            )
        return workspace.id

    return WorkspaceService.ensure_default(db, user_id).id
