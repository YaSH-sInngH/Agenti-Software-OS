from src.tools.filesystem import create_folder

def file_agent_executor(plan: dict):
    action = plan.get("action")
    parameters = plan.get("parameters", {})
    if action == "create_folder":
        folder_name = parameters.get("folder_name")
        return create_folder(folder_name)
    
    return {
        "success": False,
        "message": f"Unsupported action: {action}"
    }