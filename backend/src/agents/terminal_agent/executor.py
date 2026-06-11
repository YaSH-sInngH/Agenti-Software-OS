from src.agents.terminal_agent.tools import run_command

def terminal_agent_executor(plan: dict, context):
    action = plan.get("action")
    parameters = plan.get("parameters", {})

    if action == "run_command":
        return run_command(
            parameters.get("command"),
            context.workspace_id,
        )

    return {
        "success": False,
        "message": "Unsupported action"
    }
