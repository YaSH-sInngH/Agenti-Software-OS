import zipfile
from pathlib import Path

from src.core.utils.workspace import get_workspace_path, resolve_workspace_file


# Extensions we accept for upload. Reading / indexing / analyzing these is safe;
# executing uploaded code stays deferred until container sandboxing.
ALLOWED_EXTENSIONS = {
    ".txt", ".md", ".rst", ".log",
    ".pdf", ".docx", ".doc", ".rtf", ".odt",
    ".csv", ".tsv", ".xlsx", ".xls", ".json", ".yaml", ".yml", ".toml",
    ".ini", ".cfg", ".env", ".xml", ".html", ".htm", ".css",
    ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs",
    ".rb", ".php", ".c", ".cpp", ".cc", ".h", ".hpp", ".cs",
    ".sh", ".bash", ".ps1", ".sql", ".swift", ".kt", ".scala", ".r",
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico",
    ".zip",
}

MAX_FILE_SIZE = 25 * 1024 * 1024            # 25 MB per file
MAX_ZIP_UNCOMPRESSED = 200 * 1024 * 1024    # 200 MB total extracted
MAX_ZIP_ENTRIES = 2000                      # zip-bomb guard


class UploadError(Exception):
    pass


def _is_allowed(name: str) -> bool:
    return Path(name).suffix.lower() in ALLOWED_EXTENSIONS


def _safe_target(workspace_id: int, relative_path: str) -> Path:
    # Sandboxed absolute path; raises UploadError if it escapes the workspace.
    relative_path = (relative_path or "").replace("\\", "/").lstrip("/")
    if not relative_path:
        raise UploadError("Empty path")
    try:
        return Path(resolve_workspace_file(workspace_id, relative_path))
    except Exception:
        raise UploadError(f"Invalid path: {relative_path}")


def build_tree(workspace_id: int) -> dict:
    root = get_workspace_path(workspace_id)

    def node_for(path: Path) -> dict:
        rel = path.relative_to(root)
        node = {
            "name": path.name,
            "path": str(rel).replace("\\", "/"),
            "type": "folder" if path.is_dir() else "file",
        }
        if path.is_dir():
            node["children"] = [
                node_for(child)
                for child in sorted(
                    path.iterdir(),
                    key=lambda p: (p.is_file(), p.name.lower()),
                )
            ]
        else:
            node["size"] = path.stat().st_size
        return node

    children = [
        node_for(child)
        for child in sorted(
            root.iterdir(),
            key=lambda p: (p.is_file(), p.name.lower()),
        )
    ]

    return {
        "name": "/",
        "path": "",
        "type": "folder",
        "children": children,
    }


def save_upload(workspace_id: int, relative_path: str, content: bytes) -> str:
    if len(content) > MAX_FILE_SIZE:
        raise UploadError(
            f"{relative_path} exceeds the {MAX_FILE_SIZE // (1024 * 1024)}MB limit"
        )
    if not _is_allowed(relative_path):
        raise UploadError(f"File type not allowed: {relative_path}")

    target = _safe_target(workspace_id, relative_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)

    root = get_workspace_path(workspace_id)
    return str(target.relative_to(root)).replace("\\", "/")


def extract_zip(workspace_id: int, content: bytes, dest_prefix: str = "") -> list:
    # Safely extract a .zip: reject traversal, cap entry count and total size,
    # and skip disallowed extensions.
    import io

    written = []
    root = get_workspace_path(workspace_id)

    try:
        archive = zipfile.ZipFile(io.BytesIO(content))
    except zipfile.BadZipFile:
        raise UploadError("Invalid zip archive")

    infos = [i for i in archive.infolist() if not i.is_dir()]

    if len(infos) > MAX_ZIP_ENTRIES:
        raise UploadError("Zip has too many entries")

    total = sum(i.file_size for i in infos)
    if total > MAX_ZIP_UNCOMPRESSED:
        raise UploadError("Zip extracts to too much data")

    for info in infos:
        name = info.filename.replace("\\", "/")

        if name.startswith("/") or ".." in Path(name).parts:
            continue  # path traversal attempt
        if not _is_allowed(name):
            continue
        if info.file_size > MAX_FILE_SIZE:
            continue

        rel = f"{dest_prefix.rstrip('/')}/{name}" if dest_prefix else name
        target = _safe_target(workspace_id, rel)
        target.parent.mkdir(parents=True, exist_ok=True)

        with archive.open(info) as src:
            target.write_bytes(src.read())

        written.append(str(target.relative_to(root)).replace("\\", "/"))

    return written


def read_file_bytes(workspace_id: int, relative_path: str) -> bytes:
    target = _safe_target(workspace_id, relative_path)
    if not target.exists() or not target.is_file():
        raise UploadError("File not found")
    return target.read_bytes()


def delete_path(workspace_id: int, relative_path: str) -> bool:
    target = _safe_target(workspace_id, relative_path)
    if not target.exists():
        return False
    if target.is_dir():
        import shutil
        shutil.rmtree(target)
    else:
        target.unlink()
    return True
