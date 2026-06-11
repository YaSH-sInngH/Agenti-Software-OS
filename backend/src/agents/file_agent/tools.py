from pathlib import Path
from src.core.utils.workspace import get_workspace_path, resolve_workspace_file


def create_folder(workspace_id: int, folder_name: str):
    folder_path = Path(resolve_workspace_file(workspace_id, folder_name))
    folder_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    workspace = get_workspace_path(workspace_id)
    return {
        "success": True,
        "path": str(folder_path.relative_to(workspace)).replace("\\", "/"),
    }


def list_files(workspace_id: int):
    workspace = get_workspace_path(workspace_id)
    items = []
    for item in workspace.iterdir():
        items.append({
            "name": item.name,
            "type": "folder" if item.is_dir() else "file"
        })

    return {
        "success": True,
        'items': items
    }


def write_file(workspace_id: int, filename: str, content: str):
    file_path = Path(resolve_workspace_file(workspace_id, filename))
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(
        content,
        encoding="utf-8"
    )
    workspace = get_workspace_path(workspace_id)
    return {
        "success": True,
        "path": str(file_path.relative_to(workspace)).replace("\\", "/"),
    }


def read_file(workspace_id: int, filename: str):
    file_path = Path(resolve_workspace_file(workspace_id, filename))
    if not file_path.exists():
        return {
            "success": False,
            "message": "File does not exist"
        }

    content = file_path.read_text(
        encoding="utf-8"
    )

    return {
        "success": True,
        "content": content
    }
