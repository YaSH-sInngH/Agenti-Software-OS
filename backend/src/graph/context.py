from dataclasses import dataclass


@dataclass
class WorkspaceContext:
    # Identity + workspace scope handed to every agent executor.
    user_id: int
    workspace_id: int
