from src.agents.reminder_agent.service import ReminderService


def reminder_agent_executor(
    plan: dict,
    user_id: int
):

    action = plan.get("action")

    params = plan.get("parameters", {})

    if action == "create_reminder":
        return ReminderService.create(
            user_id,
            params.get("message"),
            params.get("remind_at"),
        )

    if action == "list_reminders":
        return ReminderService.list(user_id)

    if action == "delete_reminder":
        return ReminderService.delete(user_id, params)

    if action == "due_reminders":
        return ReminderService.due(user_id)

    if action == "daily_summary":
        return ReminderService.daily_summary(user_id)

    return {
        "success": False,
        "message": f"Unsupported action: {action}",
    }
