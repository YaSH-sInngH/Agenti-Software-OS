from pathlib import Path

WORKSPACE = Path("workspace")

def create_folder(folder_name: str):
    folder_path = WORKSPACE / folder_name
    folder_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    return {
        "success": True,
        "path": str(folder_path)
    }

def list_files():
    items = []
    for item in WORKSPACE.iterdir():
        items.append({
            "name": item.name,
            "type": "folder" if item.is_dir() else "file"
        })
    
    return {
        "success": True,
        'items': items
    }

def write_file(filename: str, content: str):
    file_path = WORKSPACE / filename
    file_path.write_text(
        content,
        encoding="utf-8"
    )
    return {
        "success": True,
        "path": str(file_path)
    }

def read_file(filename: str):
    file_path = WORKSPACE / filename
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