from src.agents.codebase_agent.service import CodebaseService


def codebase_agent_executor(
    plan: dict,
    context,
):

    action = plan.get("action")

    params = plan.get("parameters", {})

    if action == "analyze_codebase":
        return CodebaseService.analyze(
            context.workspace_id,
            params.get("path"),
        )

    return {
        "success": False,
        "message": f"Unsupported action: {action}",
    }
