from src.agents.resume_agent.service import ResumeService


def resume_agent_executor(
    plan: dict
):

    action = plan.get("action")

    params = plan.get("parameters", {})

    if action == "analyze_resumes":
        return ResumeService.analyze(
            params.get("job_description")
        )

    return {
        "success": False,
        "message": f"Unsupported action: {action}",
    }
