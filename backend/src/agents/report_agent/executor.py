from src.agents.report_agent.service import ReportService


def report_agent_executor(
    plan: dict
):

    action = plan.get("action")

    params = plan.get("parameters", {})

    if action == "generate_report":
        return ReportService.generate(
            params.get("topic"),
            params.get("format", "markdown"),
            params.get("title"),
        )

    if action == "create_report":
        return ReportService.create(
            params.get("title"),
            params.get("content"),
            params.get("format", "markdown"),
        )

    return {
        "success": False,
        "message": f"Unsupported action: {action}",
    }
