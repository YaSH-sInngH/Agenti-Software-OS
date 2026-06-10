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

    return {
        "success": False,
        "message": "Unknown action"
    }