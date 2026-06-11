from src.agents.resume_agent.service import ResumeService


def resume_agent_executor(
    plan: dict,
    context,
):

    action = plan.get("action")

    params = plan.get("parameters", {})

    if action == "analyze_resumes":
        return ResumeService.analyze(
            context.workspace_id,
            params.get("job_description"),
        )

    return {
        "success": False,
        "message": f"Unsupported action: {action}",
    }
