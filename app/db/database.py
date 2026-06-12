# app/db/database.py
"""
PostgreSQL connection using SQLAlchemy 2.0's modern declarative style.

Why PostgreSQL instead of SQLite (Project 1's choice):
  KYC records are inherently relational — a case has documents,
  screening results, decisions, and reviewer overrides, all linked
  by foreign keys. PostgreSQL's row-level locking also handles
  concurrent writes better than SQLite's file-level locking,
  which matters as the case queue grows.

Why psycopg (v3) over psycopg2:
  psycopg3 is the actively maintained successor, with native
  async support (not used yet, but available for future upgrade)
  and better type handling.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_size=5, max_overflow=10)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()


def get_db():
    """FastAPI dependency — yields a session, closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables. Called at startup — idempotent."""
    from app.db import models  # noqa: F401 — registers models with Base
    Base.metadata.create_all(bind=engine)