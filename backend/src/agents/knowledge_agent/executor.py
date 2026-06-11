from src.agents.knowledge_agent.service import (
    KnowledgeService
)


def knowledge_agent_executor(
    plan,
    context,
):

    action = plan["action"]

    params = plan["parameters"]

    workspace_id = context.workspace_id

    if action == "index_document":

        return (
            KnowledgeService
            .index_document(
                params["file_path"],
                workspace_id
            )
        )

    if action == "ask_document":

        return (
            KnowledgeService
            .ask_document(
                params["file_path"],
                params["question"],
                workspace_id
            )
        )

    if action == "ask_workspace":

        return (
            KnowledgeService
            .ask_workspace(
                params["question"],
                workspace_id
            )
        )

    if action == "search_workspace":

        return (
            KnowledgeService
            .search_workspace(
                params["query"],
                workspace_id
            )
        )

    if action == "delete_document":

        return (
            KnowledgeService
            .delete_document(
                params["file_path"],
                workspace_id
            )
        )

    if action == "reindex_document":

        return (
            KnowledgeService
            .reindex_document(
                params["file_path"],
                workspace_id
            )
        )

    return {
        "success": False,
        "message": "Unknown action"
    }
