from src.agents.task_agent.service import TaskService


def task_agent_executor(
    plan: dict,
    user_id: int
):

    action = plan.get("action")

    params = plan.get("parameters", {})

    if action == "create_task":
        return TaskService.create(
            user_id,
            params.get("title"),
            params.get("description"),
            params.get("due_date"),
        )

    if action == "list_tasks":
        return TaskService.list(user_id)

    if action == "update_task":
        return TaskService.update(user_id, params)

    if action == "complete_task":
        return TaskService.complete(user_id, params)

    if action == "delete_task":
        return TaskService.delete(user_id, params)

    return {
        "success": False,
        "message": f"Unsupported action: {action}",
    }
