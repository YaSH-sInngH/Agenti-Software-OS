from src.agents.indexer_agent.service import (
    WorkspaceIndexerService
)


def indexer_agent_executor(
    plan: dict,
    context,
):

    action = plan.get("action")

    user_id = context.user_id
    workspace_id = context.workspace_id

    if action == "index_workspace":
        return WorkspaceIndexerService.index_workspace(user_id, workspace_id)

    if action == "reindex_workspace":
        return WorkspaceIndexerService.reindex_workspace(user_id, workspace_id)

    if action == "index_workspace_background":
        return WorkspaceIndexerService.index_workspace_background(
            user_id,
            workspace_id,
        )

    if action == "index_status":
        return WorkspaceIndexerService.status(user_id, workspace_id)

    return {
        "success": False,
        "message": f"Unsupported action: {action}",
    }
