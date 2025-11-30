"""
Database configuration and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Create database engine
# SQLite doesn't support pool_pre_ping, pool_size, etc.
if settings.database_url.startswith("sqlite"):
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},  # Needed for SQLite
        echo=settings.debug,  # Log SQL queries in debug mode
    )
else:
    # PostgreSQL or other databases
    # Add connection arguments to help with IPv6/IPv4 and network issues
    connect_args = {}
    
    # Parse connection string to add parameters if not present
    db_url = settings.database_url
    if '?' not in db_url:
        # Add connection parameters to help with Railway network issues
        separator = '&' if '?' in db_url else '?'
        db_url = f"{db_url}{separator}connect_timeout=10&sslmode=require"
    
    engine = create_engine(
        db_url,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=10,
        max_overflow=20,
        echo=settings.debug,
        connect_args=connect_args,
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency for getting database session.
    Use with FastAPI Depends().
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database - create all tables.
    Call this after running Alembic migrations.
    """
    Base.metadata.create_all(bind=engine)

