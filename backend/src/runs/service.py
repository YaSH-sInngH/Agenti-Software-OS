from src.core.db.database import SessionLocal
from src.core.db.models import Run


def serialize_run(run, include_detail: bool = True):
    data = {
        "id": run.id,
        "workspace_id": run.workspace_id,
        "message": run.message,
        "status": run.status,
        "created_at": run.created_at.isoformat() if run.created_at else None,
    }
    if include_detail:
        data["plan"] = run.plan
        data["results"] = run.results
        data["response"] = run.response
    else:
        # Lightweight summary for list views.
        data["step_count"] = len(run.plan or [])
    return data


def status_for(results):
    # "partial" if any step reported failure, else "completed".
    for r in results or []:
        result = r.get("result") or {}
        if isinstance(result, dict) and result.get("success") is False:
            return "partial"
    return "completed"


class RunService:

    @staticmethod
    def create(
        user_id: int,
        workspace_id: int,
        message: str,
        plan,
        results,
        response: str,
        status: str = None,
    ):
        db = SessionLocal()
        try:
            run = Run(
                user_id=user_id,
                workspace_id=workspace_id,
                message=message,
                plan=plan,
                results=results,
                response=response,
                status=status or status_for(results),
            )
            db.add(run)
            db.commit()
            db.refresh(run)
            return serialize_run(run)
        finally:
            db.close()

    @staticmethod
    def list(user_id: int, workspace_id: int, limit: int = 20, offset: int = 0):
        db = SessionLocal()
        try:
            query = (
                db.query(Run)
                .filter(
                    Run.user_id == user_id,
                    Run.workspace_id == workspace_id,
                )
            )
            total = query.count()
            runs = (
                query.order_by(Run.created_at.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )
            return {
                "success": True,
                "runs": [serialize_run(r, include_detail=False) for r in runs],
                "total": total,
                "limit": limit,
                "offset": offset,
            }
        finally:
            db.close()

    @staticmethod
    def get(user_id: int, workspace_id: int, run_id: int):
        db = SessionLocal()
        try:
            run = (
                db.query(Run)
                .filter(
                    Run.id == run_id,
                    Run.user_id == user_id,
                    Run.workspace_id == workspace_id,
                )
                .first()
            )
            if not run:
                return None
            return serialize_run(run)
        finally:
            db.close()
