from src.agents.document_agent.tools import read_document
from src.llm.claude import llm
from src.utils.workspace import resolve_workspace_file

class DocumentService:

    @staticmethod
    def read(file_path: str):
        resolved_path=(resolve_workspace_file(file_path))
        content = read_document(resolved_path)
        return {
            "success": True,
            "content": content
        }

    @staticmethod
    def summarize(file_path: str):
        resolved_path=(resolve_workspace_file(file_path))
        content = read_document(resolved_path)
        prompt = f"""
Summarize this document.

Document:

{content[:10000]}
"""
        result = llm.invoke(
            prompt
        )
        return {
            "success": True,
            "summary": result.content
        }