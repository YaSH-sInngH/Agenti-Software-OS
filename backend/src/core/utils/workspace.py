from pathlib import Path
from src.core.config.settings import settings


def get_workspaces_root() -> Path:
    # Root that holds every per-workspace directory: workspaces/{workspace_id}/...
    root = Path(settings.WORKSPACES_ROOT)
    if not root.is_absolute():
        # Place it alongside the legacy single workspace dir.
        root = Path(settings.WORKSPACE_DIR).resolve().parent / settings.WORKSPACES_ROOT
    return root.resolve()


def get_workspace_path(workspace_id: int) -> Path:
    # Isolated directory for a single workspace. Created on demand.
    path = (get_workspaces_root() / str(workspace_id)).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def resolve_workspace_file(workspace_id: int, filename: str) -> str:
    # Resolve a workspace-relative path and refuse to escape the workspace sandbox.
    workspace = get_workspace_path(workspace_id)
    file_path = (workspace / filename).resolve()
    if file_path != workspace and workspace not in file_path.parents:
        raise Exception("Invalid workspace path")
    return str(file_path)
