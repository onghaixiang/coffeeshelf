"""Database engine + session dependency.

- Local dev: SQLite file next to backend/ (beans.db), zero config.
- Vercel/production: set DATABASE_URL (e.g. Neon Postgres) — serverless
  filesystems are ephemeral, so on-disk SQLite would lose data there. If
  DATABASE_URL is missing on Vercel we fall back to /tmp SQLite so the app
  still boots (data resets on cold starts).
"""
import os
from pathlib import Path

from sqlmodel import SQLModel, Session, create_engine


def _database_url() -> tuple[str, dict]:
    url = os.environ.get("DATABASE_URL")
    if url:
        # Neon/Heroku-style URLs say postgres://; SQLAlchemy wants postgresql://
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://"):]
        return url, {}
    if os.environ.get("VERCEL"):
        return "sqlite:////tmp/beans.db", {"check_same_thread": False}
    db_path = Path(__file__).resolve().parent.parent / "beans.db"
    return f"sqlite:///{db_path}", {"check_same_thread": False}


_url, _connect_args = _database_url()
engine = create_engine(_url, echo=False, connect_args=_connect_args)


def init_db() -> None:
    """Create tables. Import models first so they're registered on SQLModel.metadata."""
    from . import models  # noqa: F401  (registers CoffeeBean)

    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency yielding a DB session."""
    with Session(engine) as session:
        yield session
