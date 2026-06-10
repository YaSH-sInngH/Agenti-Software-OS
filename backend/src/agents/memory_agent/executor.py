from src.agents.memory_agent.service import MemoryService


def memory_agent_executor(
    plan: dict,
    user_id: int
):

    action = plan.get(
        "action"
    )

    parameters = plan.get(
        "parameters",
        {}
    )

    if action == "store_memory":
        memory = parameters.get("memory")
        if not memory:
            return {
                "success": False,
                "message": "Missing memory parameter"
            }

        return MemoryService.store(
            user_id=user_id,
            memory=parameters.get(
                "memory"
            ),
            memory_type=parameters.get(
                "memory_type",
                "user_memory"
            )
        )

    elif action == "retrieve_memory":

        return MemoryService.retrieve(
            user_id=user_id,
            query=parameters.get(
                "query"
            )
        )

    return {
        "success": False,
        "message": f"Unsupported action: {action}"
    }