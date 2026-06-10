from src.agents.indexer_agent.service import (
    WorkspaceIndexerService
)


def indexer_agent_executor(
    plan: dict,
    user_id: int
):

    action = plan.get("action")

    if action == "index_workspace":
        return WorkspaceIndexerService.index_workspace(user_id)

    if action == "reindex_workspace":
        return WorkspaceIndexerService.reindex_workspace(user_id)

    if action == "index_workspace_background":
        return WorkspaceIndexerService.index_workspace_background(
            user_id
        )

    if action == "index_status":
        return WorkspaceIndexerService.status(user_id)

    return {
        "success": False,
        "message": f"Unsupported action: {action}",
    }
