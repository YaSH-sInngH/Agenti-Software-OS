from src.core.db.database import SessionLocal
from src.core.db.models import Task, Reminder, Memory, IndexedFile
from src.agents.task_agent.service import serialize_task
from src.agents.reminder_agent.service import serialize_reminder


class DashboardService:

    @staticmethod
    def overview(user_id: int, workspace_id: int):
        db = SessionLocal()
        try:
            def scoped(model):
                return db.query(model).filter(
                    model.user_id == user_id,
                    model.workspace_id == workspace_id,
                )

            tasks_total = scoped(Task).count()
            tasks_pending = scoped(Task).filter(Task.status == "pending").count()
            reminders_total = scoped(Reminder).count()
            reminders_pending = (
                scoped(Reminder).filter(Reminder.status == "pending").count()
            )
            memories_total = scoped(Memory).count()
            indexed_total = scoped(IndexedFile).count()

            recent_tasks = (
                scoped(Task).order_by(Task.created_at.desc()).limit(5).all()
            )
            recent_reminders = (
                scoped(Reminder).order_by(Reminder.created_at.desc()).limit(5).all()
            )

            return {
                "success": True,
                "counts": {
                    "tasks_total": tasks_total,
                    "tasks_pending": tasks_pending,
                    "reminders_total": reminders_total,
                    "reminders_pending": reminders_pending,
                    "memories_total": memories_total,
                    "indexed_files": indexed_total,
                },
                "recent": {
                    "tasks": [serialize_task(t) for t in recent_tasks],
                    "reminders": [serialize_reminder(r) for r in recent_reminders],
                },
            }
        finally:
            db.close()

    @staticmethod
    def search_db(user_id: int, workspace_id: int, q: str, limit: int = 10):
        # Keyword search over tasks + memories (DB ilike). Documents are searched
        # separately via the vector store by the route.
        db = SessionLocal()
        try:
            like = f"%{q}%"

            tasks = (
                db.query(Task)
                .filter(
                    Task.user_id == user_id,
                    Task.workspace_id == workspace_id,
                    Task.title.ilike(like),
                )
                .limit(limit)
                .all()
            )

            memories = (
                db.query(Memory)
                .filter(
                    Memory.user_id == user_id,
                    Memory.workspace_id == workspace_id,
                    Memory.text.ilike(like),
                )
                .limit(limit)
                .all()
            )

            return {
                "tasks": [serialize_task(t) for t in tasks],
                "memories": [
                    {"id": m.id, "text": m.text, "type": m.type}
                    for m in memories
                ],
            }
        finally:
            db.close()
