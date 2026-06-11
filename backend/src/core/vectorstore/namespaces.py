def knowledge_namespace(workspace_id: int) -> str:
    return f"ws_{workspace_id}_knowledge"


def memory_namespace(workspace_id: int) -> str:
    return f"ws_{workspace_id}_memory"
