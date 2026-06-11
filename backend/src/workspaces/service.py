from sqlalchemy.orm import Session

from src.core.db.models import Workspace

DEFAULT_WORKSPACE_NAME = "Default Workspace"


def serialize_workspace(workspace: Workspace) -> dict:
    return {
        "id": workspace.id,
        "name": workspace.name,
        "created_at": (
            workspace.created_at.isoformat()
            if workspace.created_at
            else None
        ),
    }


class WorkspaceService:

    @staticmethod
    def list(db: Session, user_id: int):
        return (
            db.query(Workspace)
            .filter(Workspace.user_id == user_id)
            .order_by(Workspace.created_at.asc())
            .all()
        )

    @staticmethod
    def get(db: Session, user_id: int, workspace_id: int):
        # Ownership-checked lookup. Returns None if missing or not owned.
        return (
            db.query(Workspace)
            .filter(
                Workspace.id == workspace_id,
                Workspace.user_id == user_id,
            )
            .first()
        )

    @staticmethod
    def create(db: Session, user_id: int, name: str):
        workspace = Workspace(
            user_id=user_id,
            name=(name or "").strip() or DEFAULT_WORKSPACE_NAME,
        )
        db.add(workspace)
        db.commit()
        db.refresh(workspace)
        return workspace

    @staticmethod
    def rename(db: Session, workspace: Workspace, name: str):
        workspace.name = (name or "").strip() or workspace.name
        db.commit()
        db.refresh(workspace)
        return workspace

    @staticmethod
    def delete(db: Session, workspace: Workspace):
        db.delete(workspace)
        db.commit()

    @staticmethod
    def ensure_default(db: Session, user_id: int):
        # Return the user's first workspace, creating a default if they have none.
        existing = (
            db.query(Workspace)
            .filter(Workspace.user_id == user_id)
            .order_by(Workspace.created_at.asc())
            .first()
        )
        if existing:
            return existing
        return WorkspaceService.create(db, user_id, DEFAULT_WORKSPACE_NAME)
