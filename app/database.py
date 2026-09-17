"""
Database engine and session management.

This is the only file that constructs the SQLAlchemy engine. Repositories
receive a `Session` (via `get_db` in FastAPI routes, or `SessionLocal()`
directly inside agents) -- they never import or configure the engine
themselves.
"""
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class every ORM model in app/models/ inherits from."""
    pass


def get_db() -> Generator:
    """
    FastAPI dependency: `db: Session = Depends(get_db)` in route handlers.
    Guarantees the session is closed even if the request raises.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope():
    """
    Context manager for non-request code (agents, scheduler jobs):

        with session_scope() as db:
            repo = CaseRepository(db)
            ...

    Commits on success, rolls back on exception, always closes.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()