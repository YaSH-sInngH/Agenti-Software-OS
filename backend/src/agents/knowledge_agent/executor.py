from src.agents.knowledge_agent.service import (
    KnowledgeService
)


def knowledge_agent_executor(
    plan,
    user_id
):

    action = plan["action"]

    params = plan["parameters"]

    if action == "index_document":

        return (
            KnowledgeService
            .index_document(
                params["file_path"],
                user_id
            )
        )

    if action == "ask_document":

        return (
            KnowledgeService
            .ask_document(
                params["file_path"],
                params["question"],
                user_id
            )
        )

    if action == "ask_workspace":

        return (
            KnowledgeService
            .ask_workspace(
                params["question"],
                user_id
            )
        )

    if action == "delete_document":

        return (
            KnowledgeService
            .delete_document(
                params["file_path"],
                user_id
            )
        )

    if action == "reindex_document":

        return (
            KnowledgeService
            .reindex_document(
                params["file_path"],
                user_id
            )
        )

    return {
        "success": False,
        "message": "Unknown action"
    }
