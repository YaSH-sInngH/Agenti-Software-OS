import subprocess
from src.agents.terminal_agent.constants import ALLOWED_COMMANDS, BLOCKED_KEYWORDS
from src.core.utils.workspace import get_workspace_path

def run_command(command: str, workspace_id: int):
    command_parts = command.strip().split()
    if not command_parts:
        return {
            "success": False,
            "message": "Empty command"
        }
    base_command = command_parts[0]
    if base_command not in ALLOWED_COMMANDS:
        return {
            "success": False,
            "message": f"Command '{base_command}' is not allowed"
        }
    
    lower_command = command.lower()

    for keyword in BLOCKED_KEYWORDS:
        if keyword in lower_command:
            return {
                "success": False,
                "message": f"Blocked command detected: {keyword}"
            }
        
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(get_workspace_path(workspace_id))
        )

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "message": "Command timed out"
        }
    except Exception as e:
        return{
            "success": False,
            "error": str(e)
        }