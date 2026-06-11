from src.agents.file_agent.tools import create_folder, list_files, write_file, read_file

def file_agent_executor(plan: dict, context):
    action = plan.get("action")
    parameters = plan.get("parameters", {})
    workspace_id = context.workspace_id

    if action == "create_folder":
        folder_name = parameters.get("folder_name")
        return create_folder(workspace_id, folder_name)

    elif action == "list_files":
        return list_files(workspace_id)

    elif action == "write_file":
        return write_file(
            workspace_id,
            parameters.get("filename"),
            parameters.get("content"),
        )

    elif action == "read_file":
        return read_file(
            workspace_id,
            parameters.get("filename"),
        )

    return {
        "success": False,
        "message": f"Unsupported action: {action}"
    }
