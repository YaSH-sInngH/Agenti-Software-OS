from pathlib import Path

WORKSPACE = Path("workspace")

def create_folder(folder_name: str):
    folder_path = WORKSPACE / folder_name
    print("Creating folder at:", folder_path.resolve())
    folder_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    return {
        "success": True,
        "path": str(folder_path)
    }