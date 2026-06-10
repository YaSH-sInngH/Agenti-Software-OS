from src.core.utils.workspace import get_workspace_path
from src.core.llm.claude import llm


IGNORE_DIRS = {
    "node_modules",
    ".git",
    "venv",
    ".venv",
    "__pycache__",
    ".next",
    "dist",
    "build",
    ".idea",
    ".vscode",
}

MANIFESTS = {
    "package.json",
    "requirements.txt",
    "pyproject.toml",
    "Cargo.toml",
    "go.mod",
    "pom.xml",
    "composer.json",
    "Gemfile",
}

MAX_FILES = 300


def resolve_dir(path_param):

    workspace = get_workspace_path()

    if not path_param:
        return workspace

    target = (workspace / path_param).resolve()

    if not str(target).startswith(str(workspace)):
        raise Exception("Invalid workspace path")

    return target


def walk_codebase(root):

    tree = []
    manifests = {}
    count = 0

    for path in root.rglob("*"):

        if any(part in IGNORE_DIRS for part in path.parts):
            continue

        if path.is_file():
            count += 1

            if count <= MAX_FILES:
                rel = path.relative_to(root)
                tree.append(str(rel).replace("\\", "/"))

            if path.name in MANIFESTS and path.name not in manifests:
                try:
                    manifests[path.name] = (
                        path.read_text(encoding="utf-8")[:2000]
                    )
                except Exception:
                    pass

    return tree, manifests, count


class CodebaseService:

    @staticmethod
    def analyze(path: str = None):

        try:
            root = resolve_dir(path)
        except Exception as e:
            return {"success": False, "message": str(e)}

        if not root.exists() or not root.is_dir():
            return {
                "success": False,
                "message": "Directory not found",
            }

        tree, manifests, count = walk_codebase(root)

        manifest_text = "\n\n".join(
            f"--- {name} ---\n{content}"
            for name, content in manifests.items()
        ) or "(no manifest files found)"

        tree_text = "\n".join(tree[:200])

        prompt = f"""
You are a senior engineer analyzing a codebase.

Based on the file tree and manifest files below:
1. Summarize the project structure.
2. Identify the tech stack.
3. Give a few concrete improvement suggestions.

File tree (showing {len(tree[:200])} of {count} files):

{tree_text}

Manifest files:

{manifest_text}
"""

        result = llm.invoke(prompt)

        return {
            "success": True,
            "root": str(root),
            "file_count": count,
            "analysis": result.content,
        }
