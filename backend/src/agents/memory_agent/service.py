from src.core.db.database import SessionLocal
from src.core.db.models import Memory
from src.core.vectorstore.memory_store import (
    store_memory,
    retrieve_memory,
    delete_memory_vector,
)


def serialize_memory(memory):
    return {
        "id": memory.id,
        "text": memory.text,
        "type": memory.type,
        "created_at": (
            memory.created_at.isoformat()
            if memory.created_at
            else None
        ),
    }


class MemoryService:

    @staticmethod
    def store(
        user_id: int,
        workspace_id: int,
        memory: str,
        memory_type: str,
    ):
        result = store_memory(
            user_id,
            workspace_id,
            memory,
            memory_type,
        )

        db = SessionLocal()
        try:
            row = Memory(
                user_id=user_id,
                workspace_id=workspace_id,
                vector_id=result.get("memory_id"),
                text=memory,
                type=memory_type,
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            result["id"] = row.id
        finally:
            db.close()

        return result

    @staticmethod
    def retrieve(
        user_id: int,
        workspace_id: int,
        query: str,
    ):
        return retrieve_memory(
            user_id,
            workspace_id,
            query,
        )

    @staticmethod
    def list(user_id: int, workspace_id: int):
        db = SessionLocal()
        try:
            rows = (
                db.query(Memory)
                .filter(
                    Memory.user_id == user_id,
                    Memory.workspace_id == workspace_id,
                )
                .order_by(Memory.created_at.desc())
                .all()
            )
            return {
                "success": True,
                "memories": [serialize_memory(m) for m in rows],
            }
        finally:
            db.close()

    @staticmethod
    def delete(user_id: int, workspace_id: int, memory_id: int):
        db = SessionLocal()
        try:
            row = (
                db.query(Memory)
                .filter(
                    Memory.id == memory_id,
                    Memory.user_id == user_id,
                    Memory.workspace_id == workspace_id,
                )
                .first()
            )

            if not row:
                return {
                    "success": False,
                    "message": "Memory not found",
                }

            if row.vector_id:
                try:
                    delete_memory_vector(workspace_id, row.vector_id)
                except Exception:
                    pass

            db.delete(row)
            db.commit()

            return {
                "success": True,
                "message": "Memory deleted",
            }
        finally:
            db.close()
