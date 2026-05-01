from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from train_core.config import ROOT_DIR, settings


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
    from train_core import models  # noqa: F401

    alembic_config = Config(str(ROOT_DIR / "alembic.ini"))
    alembic_config.set_main_option("script_location", str(ROOT_DIR / "migrations"))
    alembic_config.set_main_option("sqlalchemy.url", settings.database_url)

    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    managed_tables = {"run_records", "project_states"}

    if "alembic_version" not in table_names:
        if managed_tables.issubset(table_names):
            command.stamp(alembic_config, "head")
        elif managed_tables & table_names:
            raise RuntimeError(
                "Partial legacy database detected. Remove the local SQLite file and rerun startup."
            )

    command.upgrade(alembic_config, "head")
