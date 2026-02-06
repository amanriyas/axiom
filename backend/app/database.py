# app/database.py
"""SQLAlchemy database engine, session, and Base for ORM models."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

# ── Engine ───────────────────────────────────────────────────
# connect_args needed for SQLite to allow multi-thread access
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=settings.DEBUG,
)

# ── Session factory ──────────────────────────────────────────
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ── Declarative Base ─────────────────────────────────────────
Base = declarative_base()


# ── Dependency ───────────────────────────────────────────────
def get_db():
    """FastAPI dependency that yields a DB session and closes it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Table creation ───────────────────────────────────────────
def create_tables():
    """Create all tables defined by ORM models. Called on app startup."""
    Base.metadata.create_all(bind=engine)
