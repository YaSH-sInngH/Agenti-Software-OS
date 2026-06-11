from dataclasses import dataclass
from typing import Optional

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from src.core.db.database import get_db
from src.auth.dependencies import get_current_user
from src.workspaces.resolver import resolve_workspace_id


@dataclass
class Scope:
    user_id: int
    workspace_id: int


def get_scope(
    workspace_id: Optional[int] = Query(None),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Scope:
    # Resolves the active workspace from the ?workspace_id= query param,
    # validating ownership, or falling back to the user's default workspace.
    resolved = resolve_workspace_id(db, current_user.id, workspace_id)
    return Scope(user_id=current_user.id, workspace_id=resolved)
