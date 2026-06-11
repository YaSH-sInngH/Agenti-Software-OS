from src.agents.browser_agent.service import BrowserService


def browser_agent_executor(
    plan: dict,
    context,
):

    action = plan.get("action")

    params = plan.get("parameters", {})

    if action == "open_website":
        return BrowserService.open_website(
            params.get("url")
        )

    if action == "web_search":
        return BrowserService.web_search(
            params.get("query")
        )

    if action == "extract_data":
        return BrowserService.extract_data(
            params.get("url"),
            params.get("selector"),
        )

    return {
        "success": False,
        "message": f"Unsupported action: {action}",
    }
