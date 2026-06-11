from src.agents.report_agent.service import ReportService


def report_agent_executor(
    plan: dict,
    context,
):

    action = plan.get("action")

    params = plan.get("parameters", {})

    workspace_id = context.workspace_id

    if action == "generate_report":
        return ReportService.generate(
            workspace_id,
            params.get("topic"),
            params.get("format", "markdown"),
            params.get("title"),
        )

    if action == "create_report":
        return ReportService.create(
            workspace_id,
            params.get("title"),
            params.get("content"),
            params.get("format", "markdown"),
        )

    return {
        "success": False,
        "message": f"Unsupported action: {action}",
    }
