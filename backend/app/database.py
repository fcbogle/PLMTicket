import os
from pathlib import Path

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool


DEFAULT_SQLITE_PATH = Path(__file__).resolve().parents[1] / "plm_tickets.db"
DATABASE_URL = os.getenv("PLM_DATABASE_URL", f"sqlite:///{DEFAULT_SQLITE_PATH}")


Base = declarative_base()


engine_kwargs: dict[str, object] = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {
        "check_same_thread": False,
        "timeout": int(os.getenv("PLM_SQLITE_BUSY_TIMEOUT_SECONDS", "30")),
    }
    # A mounted SQLite file on Azure File Share is less stable with pooled connections.
    engine_kwargs["poolclass"] = NullPool

engine = create_engine(DATABASE_URL, pool_pre_ping=True, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def ensure_ticket_schema() -> None:
    inspector = inspect(engine)
    if "tickets" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("tickets")}
    if "ticket_type" in columns:
        return

    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE tickets ADD COLUMN ticket_type VARCHAR(100)"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
