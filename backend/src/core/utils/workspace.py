from pathlib import Path
from src.core.config.settings import settings

def get_workspace_path() -> Path:
    return Path(settings.WORKSPACE_DIR).resolve()


def resolve_workspace_file(filename: str) -> str:

    workspace = get_workspace_path()
    file_path = (
        workspace / filename
    ).resolve()
    if not str(file_path).startswith(
        str(workspace)
    ):
        raise Exception("Invalid workspace path")
    return str(file_path)