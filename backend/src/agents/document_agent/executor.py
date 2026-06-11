from src.agents.document_agent.service import DocumentService

def document_agent_executor(
    plan: dict,
    context,
):
    action = plan.get("action")

    parameters = plan.get(
        "parameters",
        {}
    )

    file_path = parameters.get("file_path")
    workspace_id = context.workspace_id

    if action == "read_document":
        return DocumentService.read(workspace_id, file_path)

    if action == "summarize_document":
        return DocumentService.summarize(workspace_id, file_path)

    return {
        "success": False,
        "message": f"Unsupported action: {action}"
    }
