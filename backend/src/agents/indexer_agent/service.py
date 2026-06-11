import hashlib
import threading
from datetime import datetime

from src.core.db.database import SessionLocal
from src.core.db.models import IndexedFile
from src.core.utils.workspace import get_workspace_path
from src.agents.knowledge_agent.service import KnowledgeService


SUPPORTED = {".txt", ".pdf", ".docx"}


def list_supported_files(workspace_id: int):

    workspace = get_workspace_path(workspace_id)

    files = []

    for path in workspace.rglob("*"):
        if path.is_file() and path.suffix.lower() in SUPPORTED:
            rel = path.relative_to(workspace)
            files.append(str(rel).replace("\\", "/"))

    return files


def file_hash(path):

    digest = hashlib.md5()

    with open(path, "rb") as f:
        digest.update(f.read())

    return digest.hexdigest()


class WorkspaceIndexerService:

    @staticmethod
    def record_file(user_id: int, workspace_id: int, rel_path: str):
        # Idempotently record/update an IndexedFile row so /knowledge/status
        # reflects documents indexed directly (not just via index_workspace).
        abs_path = get_workspace_path(workspace_id) / rel_path
        if not abs_path.is_file():
            return

        digest = file_hash(abs_path)

        db = SessionLocal()
        try:
            record = (
                db.query(IndexedFile)
                .filter(
                    IndexedFile.user_id == user_id,
                    IndexedFile.workspace_id == workspace_id,
                    IndexedFile.file_path == rel_path,
                )
                .first()
            )
            if record:
                record.file_hash = digest
                record.indexed_at = datetime.utcnow()
            else:
                db.add(
                    IndexedFile(
                        user_id=user_id,
                        workspace_id=workspace_id,
                        file_path=rel_path,
                        file_hash=digest,
                        indexed_at=datetime.utcnow(),
                    )
                )
            db.commit()
        finally:
            db.close()

    @staticmethod
    def index_workspace(user_id: int, workspace_id: int, force: bool = False):

        workspace = get_workspace_path(workspace_id)
        files = list_supported_files(workspace_id)

        db = SessionLocal()

        indexed = []
        skipped = []

        try:
            for rel in files:

                digest = file_hash(workspace / rel)

                record = (
                    db.query(IndexedFile)
                    .filter(
                        IndexedFile.user_id == user_id,
                        IndexedFile.workspace_id == workspace_id,
                        IndexedFile.file_path == rel,
                    )
                    .first()
                )

                if record and record.file_hash == digest and not force:
                    skipped.append(rel)
                    continue

                if record:
                    KnowledgeService.reindex_document(rel, workspace_id)
                    record.file_hash = digest
                    record.indexed_at = datetime.utcnow()
                else:
                    KnowledgeService.index_document(rel, workspace_id)
                    db.add(
                        IndexedFile(
                            user_id=user_id,
                            workspace_id=workspace_id,
                            file_path=rel,
                            file_hash=digest,
                            indexed_at=datetime.utcnow(),
                        )
                    )

                indexed.append(rel)

            db.commit()

            return {
                "success": True,
                "indexed": indexed,
                "skipped": skipped,
                "total": len(files),
            }
        finally:
            db.close()

    @staticmethod
    def reindex_workspace(user_id: int, workspace_id: int):
        return WorkspaceIndexerService.index_workspace(
            user_id,
            workspace_id,
            force=True,
        )

    @staticmethod
    def index_workspace_background(user_id: int, workspace_id: int):

        thread = threading.Thread(
            target=WorkspaceIndexerService.index_workspace,
            args=(user_id, workspace_id),
            daemon=True,
        )
        thread.start()

        return {
            "success": True,
            "message": "Background indexing started",
        }

    @staticmethod
    def status(user_id: int, workspace_id: int):

        db = SessionLocal()

        try:
            records = (
                db.query(IndexedFile)
                .filter(
                    IndexedFile.user_id == user_id,
                    IndexedFile.workspace_id == workspace_id,
                )
                .all()
            )

            return {
                "success": True,
                "indexed_files": [
                    {
                        "file_path": r.file_path,
                        "indexed_at": (
                            r.indexed_at.isoformat()
                            if r.indexed_at
                            else None
                        ),
                    }
                    for r in records
                ],
            }
        finally:
            db.close()
