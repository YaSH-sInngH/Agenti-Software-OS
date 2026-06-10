from src.agents.document_agent.service import DocumentService

def document_agent_executor(
    plan: dict
):
    action = plan.get("action")

    parameters = plan.get(
        "parameters",
        {}
    )

    file_path = parameters.get("file_path")

    if action == "read_document":
        return DocumentService.read(file_path)

    if action == "summarize_document":
        return DocumentService.summarize(file_path)

    return {
        "success": False,
        "message": f"Unsupported action: {action}"
    }