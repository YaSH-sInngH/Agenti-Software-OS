from datetime import datetime, date

from src.core.db.database import SessionLocal
from src.core.db.models import Reminder, Task


def parse_datetime(value):

    if not value:
        return None

    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


def serialize_reminder(reminder):

    return {
        "id": reminder.id,
        "message": reminder.message,
        "remind_at": (
            reminder.remind_at.isoformat()
            if reminder.remind_at
            else None
        ),
        "status": reminder.status,
    }


class ReminderService:

    @staticmethod
    def find_reminder(db, user_id, workspace_id, params):

        query = (
            db.query(Reminder)
            .filter(
                Reminder.user_id == user_id,
                Reminder.workspace_id == workspace_id,
            )
        )

        reminder_id = params.get("reminder_id")

        if reminder_id is not None:
            return query.filter(
                Reminder.id == reminder_id
            ).first()

        text = params.get("reminder")

        if text:
            return query.filter(
                Reminder.message.ilike(f"%{text}%")
            ).first()

        return None

    @staticmethod
    def create(user_id: int, workspace_id: int, message: str, remind_at: str = None):

        db = SessionLocal()

        try:
            reminder = Reminder(
                user_id=user_id,
                workspace_id=workspace_id,
                message=message,
                remind_at=parse_datetime(remind_at),
                status="pending",
            )

            db.add(reminder)
            db.commit()
            db.refresh(reminder)

            return {
                "success": True,
                "reminder": serialize_reminder(reminder),
            }
        finally:
            db.close()

    SORT_COLUMNS = {
        "remind_at": Reminder.remind_at,
        "created_at": Reminder.created_at,
        "status": Reminder.status,
    }

    @staticmethod
    def list(
        user_id: int,
        workspace_id: int,
        status: str = None,
        sort: str = "remind_at",
        order: str = "asc",
        limit: int = None,
        offset: int = 0,
    ):

        db = SessionLocal()

        try:
            query = (
                db.query(Reminder)
                .filter(
                    Reminder.user_id == user_id,
                    Reminder.workspace_id == workspace_id,
                )
            )

            if status:
                query = query.filter(Reminder.status == status)

            total = query.count()

            column = ReminderService.SORT_COLUMNS.get(sort, Reminder.remind_at)
            query = query.order_by(
                column.desc() if order == "desc" else column.asc()
            )

            if offset:
                query = query.offset(offset)
            if limit is not None:
                query = query.limit(limit)

            reminders = query.all()

            return {
                "success": True,
                "reminders": [
                    serialize_reminder(r)
                    for r in reminders
                ],
                "total": total,
                "limit": limit,
                "offset": offset,
            }
        finally:
            db.close()

    @staticmethod
    def delete(user_id: int, workspace_id: int, params: dict):

        db = SessionLocal()

        try:
            reminder = ReminderService.find_reminder(
                db, user_id, workspace_id, params
            )

            if not reminder:
                return {
                    "success": False,
                    "message": "Reminder not found",
                }

            message = reminder.message

            db.delete(reminder)
            db.commit()

            return {
                "success": True,
                "message": f"Deleted reminder: {message}",
            }
        finally:
            db.close()

    @staticmethod
    def due(user_id: int, workspace_id: int):

        db = SessionLocal()

        try:
            now = datetime.utcnow()

            reminders = (
                db.query(Reminder)
                .filter(
                    Reminder.user_id == user_id,
                    Reminder.workspace_id == workspace_id,
                    Reminder.status == "pending",
                    Reminder.remind_at.isnot(None),
                    Reminder.remind_at <= now,
                )
                .all()
            )

            return {
                "success": True,
                "due": [
                    serialize_reminder(r)
                    for r in reminders
                ],
            }
        finally:
            db.close()

    @staticmethod
    def daily_summary(user_id: int, workspace_id: int):

        db = SessionLocal()

        try:
            today = date.today()
            end_of_day = datetime(
                today.year, today.month, today.day, 23, 59, 59
            )

            tasks = (
                db.query(Task)
                .filter(
                    Task.user_id == user_id,
                    Task.workspace_id == workspace_id,
                    Task.status == "pending",
                )
                .all()
            )

            tasks_today = [
                {
                    "title": t.title,
                    "due_date": t.due_date.isoformat(),
                    "status": t.status,
                }
                for t in tasks
                if t.due_date and t.due_date <= end_of_day
            ]

            reminders = (
                db.query(Reminder)
                .filter(
                    Reminder.user_id == user_id,
                    Reminder.workspace_id == workspace_id,
                    Reminder.status == "pending",
                )
                .all()
            )

            reminders_today = [
                serialize_reminder(r)
                for r in reminders
                if r.remind_at and r.remind_at <= end_of_day
            ]

            return {
                "success": True,
                "date": today.isoformat(),
                "tasks": tasks_today,
                "reminders": reminders_today,
            }
        finally:
            db.close()
