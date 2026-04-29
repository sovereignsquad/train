from pathlib import Path

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from autotrain_core.config import settings


class Base(DeclarativeBase):
    pass


def _ensure_sqlite_parent(url: str) -> None:
    prefix = "sqlite:///"
    if not url.startswith(prefix):
        return
    db_path = Path(url[len(prefix) :])
    db_path.parent.mkdir(parents=True, exist_ok=True)


_ensure_sqlite_parent(settings.database_url)

engine = create_engine(settings.database_url, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from autotrain_core import models  # noqa: F401

    inspector = inspect(engine)
    expected_columns = {
        "id",
        "project_key",
        "title",
        "objective",
        "metric_name",
        "metric_direction",
        "metric_value",
        "budget_seconds",
        "status",
        "mutable_artifact",
        "runner_key",
        "ratchet_decision",
        "git_action",
        "best_metric_before",
        "best_metric_after",
        "git_head_before",
        "git_head_after",
        "git_worktree_dirty",
        "started_at",
        "finished_at",
        "result_summary",
        "error_message",
        "created_at",
        "updated_at",
    }

    if inspector.has_table("run_records"):
        existing_columns = {column["name"] for column in inspector.get_columns("run_records")}
        if existing_columns != expected_columns:
            Base.metadata.drop_all(bind=engine)

    if inspector.has_table("project_states"):
        expected_project_state_columns = {
            "project_key",
            "metric_name",
            "metric_direction",
            "best_run_id",
            "best_metric_value",
            "last_run_id",
            "git_head",
            "git_worktree_dirty",
            "updated_at",
        }
        existing_columns = {column["name"] for column in inspector.get_columns("project_states")}
        if existing_columns != expected_project_state_columns:
            Base.metadata.drop_all(bind=engine)

    Base.metadata.create_all(bind=engine)
