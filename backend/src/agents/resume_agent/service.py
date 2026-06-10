from src.agents.document_agent.tools import read_document
from src.core.utils.workspace import get_workspace_path
from src.core.llm.claude import llm


SUPPORTED = {".txt", ".pdf", ".docx"}


def find_resumes():

    workspace = get_workspace_path()

    resumes = []
    documents = []

    for path in workspace.rglob("*"):
        if path.is_file() and path.suffix.lower() in SUPPORTED:
            documents.append(path)
            name = path.name.lower()
            if "resume" in name or "cv" in name:
                resumes.append(path)

    # Prefer files that look like resumes; otherwise analyze all documents.
    return resumes or documents


class ResumeService:

    @staticmethod
    def analyze(job_description: str = None):

        workspace = get_workspace_path()
        files = find_resumes()

        if not files:
            return {
                "success": False,
                "message": "No resume documents found in the workspace",
            }

        sections = []

        for path in files:
            try:
                text = read_document(str(path))
            except Exception as e:
                text = f"(could not read: {e})"

            rel = path.relative_to(workspace)
            sections.append(f"--- {rel} ---\n{text[:4000]}")

        joined = "\n\n".join(sections)

        job_block = (
            f"\nJob description to match against:\n{job_description}\n"
            if job_description
            else ""
        )

        prompt = f"""
You are a resume analyst. Analyze the resumes below.

For each resume:
- Extract the key skills.
- Summarize the experience level.

Then rank the candidates from strongest to weakest and explain the ranking briefly.
{job_block}
Resumes:

{joined}
"""

        result = llm.invoke(prompt)

        return {
            "success": True,
            "files": [
                str(p.relative_to(workspace))
                for p in files
            ],
            "analysis": result.content,
        }
