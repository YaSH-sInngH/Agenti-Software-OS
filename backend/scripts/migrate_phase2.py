"""
Phase 2 migration: single-folder -> multi-workspace.

Idempotent. Safe to re-run.

Steps:
  1. Create new tables (workspaces, memories) + anything else missing.
  2. Add workspace_id columns to tasks / reminders / indexed_files.
  3. Create a "Default Workspace" for every user that has none.
  4. Backfill workspace_id on existing rows from each user's default workspace.
  5. Enforce NOT NULL on the backfilled columns.
  6. Move legacy workspace/ contents into the earliest user's default workspace dir.

Run from the backend directory:
    venv/Scripts/python.exe -m scripts.migrate_phase2
"""

import shutil
from pathlib import Path

from sqlalchemy import text

from src.core.db.database import Base, engine, SessionLocal
from src.core.db import models  # noqa: F401  (register models on Base)
from src.core.db.models import User, Workspace
from src.core.config.settings import settings
from src.core.utils.workspace import get_workspace_path
from src.workspaces.service import WorkspaceService


SCOPED_TABLES = ("tasks", "reminders", "indexed_files")


def create_tables():
    print("1. Creating missing tables (workspaces, memories, ...)")
    Base.metadata.create_all(bind=engine)


def add_workspace_columns():
    print("2. Adding workspace_id columns where missing")
    with engine.begin() as conn:
        for table in SCOPED_TABLES:
            conn.execute(text(
                f"ALTER TABLE {table} "
                f"ADD COLUMN IF NOT EXISTS workspace_id INTEGER"
            ))
            conn.execute(text(
                f"CREATE INDEX IF NOT EXISTS "
                f"ix_{table}_workspace_id ON {table} (workspace_id)"
            ))


def ensure_default_workspaces():
    print("3. Ensuring every user has a default workspace")
    db = SessionLocal()
    created = 0
    try:
        users = db.query(User).all()
        for user in users:
            existing = (
                db.query(Workspace)
                .filter(Workspace.user_id == user.id)
                .count()
            )
            if existing == 0:
                WorkspaceService.create(db, user.id, "Default Workspace")
                created += 1
        print(f"   created {created} default workspace(s)")
    finally:
        db.close()


def backfill_workspace_ids():
    print("4. Backfilling workspace_id on existing rows")
    with engine.begin() as conn:
        # Each user's earliest workspace is their default.
        default_map = conn.execute(text(
            """
            SELECT DISTINCT ON (user_id) user_id, id
            FROM workspaces
            ORDER BY user_id, created_at ASC, id ASC
            """
        )).fetchall()

        defaults = {row.user_id: row.id for row in default_map}

        for user_id, workspace_id in defaults.items():
            for table in SCOPED_TABLES:
                conn.execute(
                    text(
                        f"UPDATE {table} SET workspace_id = :ws "
                        f"WHERE user_id = :uid AND workspace_id IS NULL"
                    ),
                    {"ws": workspace_id, "uid": user_id},
                )


def enforce_not_null():
    print("5. Enforcing NOT NULL on workspace_id columns")
    with engine.begin() as conn:
        for table in SCOPED_TABLES:
            remaining = conn.execute(text(
                f"SELECT COUNT(*) FROM {table} WHERE workspace_id IS NULL"
            )).scalar()
            if remaining:
                print(
                    f"   ! {table}: {remaining} rows still NULL "
                    f"(orphan user_id?), leaving column nullable"
                )
                continue
            conn.execute(text(
                f"ALTER TABLE {table} ALTER COLUMN workspace_id SET NOT NULL"
            ))


def move_legacy_files():
    print("6. Moving legacy workspace/ contents into a default workspace")
    legacy = Path(settings.WORKSPACE_DIR)
    if not legacy.exists() or not any(legacy.iterdir()):
        print("   no legacy workspace contents to move")
        return

    db = SessionLocal()
    try:
        target_ws = (
            db.query(Workspace)
            .order_by(Workspace.user_id.asc(), Workspace.created_at.asc())
            .first()
        )
        if not target_ws:
            print("   no workspace to move files into; skipping")
            return

        dest = get_workspace_path(target_ws.id)

        # Avoid moving the new workspaces root into itself.
        workspaces_root = dest.parent
        moved = 0
        for item in list(legacy.iterdir()):
            if item.resolve() == workspaces_root.resolve():
                continue
            target = dest / item.name
            if target.exists():
                print(f"   skip (exists): {item.name}")
                continue
            shutil.move(str(item), str(target))
            moved += 1

        print(f"   moved {moved} item(s) into workspace {target_ws.id}")
    finally:
        db.close()


def main():
    create_tables()
    add_workspace_columns()
    ensure_default_workspaces()
    backfill_workspace_ids()
    enforce_not_null()
    move_legacy_files()
    print("\nPhase 2 migration complete.")


if __name__ == "__main__":
    main()
