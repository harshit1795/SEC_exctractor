"""
Database configuration and session management.

Supports:
  - SQLite (local development fallback)
  - PostgreSQL via Supabase:
      Session pooler  (port 5432) — local dev, Alembic migrations
      Transaction pooler (port 6543) — Render/serverless production
"""
from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
import logging

logger = logging.getLogger(__name__)


def _build_engine():
    db_url = settings.database_url

    # ── SQLite (local fallback) ───────────────────────────────────────────────
    if db_url.startswith("sqlite"):
        logger.info("Using SQLite database")
        return create_engine(
            db_url,
            connect_args={"check_same_thread": False},
            echo=settings.debug,
        )

    # ── PostgreSQL / Supabase ─────────────────────────────────────────────────
    # Ensure SSL is enabled (Supabase requires it)
    if "sslmode" not in db_url:
        separator = "&" if "?" in db_url else "?"
        db_url = f"{db_url}{separator}sslmode=require"

    # Detect Transaction pooler by port (6543).
    # Transaction mode does NOT support prepared statements —
    # setting PGBOUNCER-style options tells psycopg2 to use simple queries.
    is_transaction_pooler = ":6543/" in db_url

    connect_args = {}
    if is_transaction_pooler:
        # Disable server-side prepared statements for PgBouncer / Supavisor
        # transaction mode. psycopg2 uses `prepare_threshold=None` for this.
        connect_args["options"] = "-c statement_cache_size=0"
        logger.info("Using Supabase Transaction pooler (port 6543) — prepared statements disabled")
    else:
        logger.info("Using Supabase Session pooler / direct connection (port 5432)")

    # Pool sizing: keep small on free-tier Supabase (max 60 connections total)
    engine = create_engine(
        db_url,
        pool_pre_ping=True,      # validate connections before checkout
        pool_size=5,             # keep warm connections
        max_overflow=10,         # burst headroom
        pool_timeout=30,
        pool_recycle=1800,       # recycle every 30 min to avoid stale conns
        echo=settings.debug,
        connect_args=connect_args,
    )

    return engine


# ── Module-level singletons ───────────────────────────────────────────────────

engine = _build_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ── FastAPI dependency ────────────────────────────────────────────────────────

def get_db():
    """
    Dependency for getting a database session.
    Use with FastAPI Depends().
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Create all tables (call only when NOT using Alembic migrations).
    In production, always prefer `alembic upgrade head`.
    """
    Base.metadata.create_all(bind=engine)
