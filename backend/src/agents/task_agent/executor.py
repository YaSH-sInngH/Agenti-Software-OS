from src.agents.task_agent.service import TaskService


def task_agent_executor(
    plan: dict,
    context,
):

    action = plan.get("action")

    params = plan.get("parameters", {})

    user_id = context.user_id
    workspace_id = context.workspace_id

    if action == "create_task":
        return TaskService.create(
            user_id,
            workspace_id,
            params.get("title"),
            params.get("description"),
            params.get("due_date"),
        )

    if action == "list_tasks":
        return TaskService.list(user_id, workspace_id)

    if action == "update_task":
        return TaskService.update(user_id, workspace_id, params)

    if action == "complete_task":
        return TaskService.complete(user_id, workspace_id, params)

    if action == "delete_task":
        return TaskService.delete(user_id, workspace_id, params)

    return {
        "success": False,
        "message": f"Unsupported action: {action}",
    }
