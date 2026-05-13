from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
from dotenv import load_dotenv
import os

load_dotenv()

# ── AIRA DATABASE CONNECTION MANAGER ──

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./aira.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args     = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    poolclass        = StaticPool if "sqlite" in DATABASE_URL else None,
    echo             = os.getenv("DEBUG", "False").lower() == "true"
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.
    Automatically closes session after request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """
    Create all database tables on startup.
    Safe to run multiple times — only creates tables if they don't exist.
    """
    from database.models import Base
    Base.metadata.create_all(bind=engine)
    print("AIRA database tables initialised.")


def check_database_health() -> dict:
    """Check if database connection is healthy."""
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "healthy", "database": DATABASE_URL.split("///")[0]}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


if __name__ == "__main__":
    print("Testing Database Connection...")
    health = check_database_health()
    print(f"Database health: {health}")
    init_database()
    print("Database initialised successfully!")
