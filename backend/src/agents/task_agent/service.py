from datetime import datetime

from src.core.db.database import SessionLocal
from src.core.db.models import Task


def parse_due_date(value):

    if not value:
        return None

    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


def serialize_task(task):

    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "due_date": (
            task.due_date.isoformat()
            if task.due_date
            else None
        ),
    }


class TaskService:

    @staticmethod
    def find_task(db, user_id, workspace_id, params):

        query = (
            db.query(Task)
            .filter(
                Task.user_id == user_id,
                Task.workspace_id == workspace_id,
            )
        )

        task_id = params.get("task_id")

        if task_id is not None:
            return query.filter(
                Task.id == task_id
            ).first()

        name = params.get("task")

        if name:
            return query.filter(
                Task.title.ilike(f"%{name}%")
            ).first()

        return None

    @staticmethod
    def create(
        user_id: int,
        workspace_id: int,
        title: str,
        description: str = None,
        due_date: str = None,
    ):

        db = SessionLocal()

        try:
            task = Task(
                user_id=user_id,
                workspace_id=workspace_id,
                title=title,
                description=description,
                status="pending",
                due_date=parse_due_date(due_date),
            )

            db.add(task)
            db.commit()
            db.refresh(task)

            return {
                "success": True,
                "task": serialize_task(task),
            }
        finally:
            db.close()

    SORT_COLUMNS = {
        "created_at": Task.created_at,
        "due_date": Task.due_date,
        "title": Task.title,
        "status": Task.status,
    }

    @staticmethod
    def list(
        user_id: int,
        workspace_id: int,
        status: str = None,
        sort: str = "created_at",
        order: str = "desc",
        limit: int = None,
        offset: int = 0,
    ):

        db = SessionLocal()

        try:
            query = (
                db.query(Task)
                .filter(
                    Task.user_id == user_id,
                    Task.workspace_id == workspace_id,
                )
            )

            if status:
                query = query.filter(Task.status == status)

            total = query.count()

            column = TaskService.SORT_COLUMNS.get(sort, Task.created_at)
            query = query.order_by(
                column.desc() if order == "desc" else column.asc()
            )

            if offset:
                query = query.offset(offset)
            if limit is not None:
                query = query.limit(limit)

            tasks = query.all()

            return {
                "success": True,
                "tasks": [
                    serialize_task(t)
                    for t in tasks
                ],
                "total": total,
                "limit": limit,
                "offset": offset,
            }
        finally:
            db.close()

    @staticmethod
    def update(user_id: int, workspace_id: int, params: dict):

        db = SessionLocal()

        try:
            task = TaskService.find_task(
                db, user_id, workspace_id, params
            )

            if not task:
                return {
                    "success": False,
                    "message": "Task not found",
                }

            if params.get("title"):
                task.title = params["title"]

            if "description" in params:
                task.description = params["description"]

            if "due_date" in params:
                task.due_date = parse_due_date(
                    params["due_date"]
                )

            if params.get("status"):
                task.status = params["status"]

            db.commit()
            db.refresh(task)

            return {
                "success": True,
                "task": serialize_task(task),
            }
        finally:
            db.close()

    @staticmethod
    def complete(user_id: int, workspace_id: int, params: dict):

        db = SessionLocal()

        try:
            task = TaskService.find_task(
                db, user_id, workspace_id, params
            )

            if not task:
                return {
                    "success": False,
                    "message": "Task not found",
                }

            task.status = "completed"

            db.commit()
            db.refresh(task)

            return {
                "success": True,
                "task": serialize_task(task),
            }
        finally:
            db.close()

    @staticmethod
    def delete(user_id: int, workspace_id: int, params: dict):

        db = SessionLocal()

        try:
            task = TaskService.find_task(
                db, user_id, workspace_id, params
            )

            if not task:
                return {
                    "success": False,
                    "message": "Task not found",
                }

            title = task.title

            db.delete(task)
            db.commit()

            return {
                "success": True,
                "message": f"Deleted task: {title}",
            }
        finally:
            db.close()
