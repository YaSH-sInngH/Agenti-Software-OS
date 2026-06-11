from src.agents.reminder_agent.service import ReminderService


def reminder_agent_executor(
    plan: dict,
    context,
):

    action = plan.get("action")

    params = plan.get("parameters", {})

    user_id = context.user_id
    workspace_id = context.workspace_id

    if action == "create_reminder":
        return ReminderService.create(
            user_id,
            workspace_id,
            params.get("message"),
            params.get("remind_at"),
        )

    if action == "list_reminders":
        return ReminderService.list(user_id, workspace_id)

    if action == "delete_reminder":
        return ReminderService.delete(user_id, workspace_id, params)

    if action == "due_reminders":
        return ReminderService.due(user_id, workspace_id)

    if action == "daily_summary":
        return ReminderService.daily_summary(user_id, workspace_id)

    return {
        "success": False,
        "message": f"Unsupported action: {action}",
    }
