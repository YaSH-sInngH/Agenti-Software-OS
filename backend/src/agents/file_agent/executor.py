from src.tools.filesystem import create_folder, list_files, write_file, read_file

def file_agent_executor(plan: dict):
    action = plan.get("action")
    parameters = plan.get("parameters", {})
    if action == "create_folder":
        folder_name = parameters.get("folder_name")
        return create_folder(folder_name)
    
    elif action == "list_files":
        return list_files()
    
    elif action == "write_file":
        return write_file(
            parameters.get("filename"),
            parameters.get("content"),
        )
    
    elif action == "read_file":
        return read_file(
            parameters.get("filename")
        )

    return {
        "success": False,
        "message": f"Unsupported action: {action}"
    }