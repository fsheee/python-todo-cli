"""Database connection and session management for Neon PostgreSQL."""

import os
from sqlmodel import SQLModel, Session, create_engine
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Use SQLite for local development if no DATABASE_URL is set
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./todo.db"
    engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
else:
    # Use psycopg2-binary driver (already installed)
    # Configure for Neon serverless with connection pool settings
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,  # Test connections before use (critical for Neon)
        pool_recycle=300,    # Recycle connections after 5 minutes
        pool_size=10,        # Connection pool size
        max_overflow=20      # Allow overflow connections
    )


def create_db_and_tables():
    """Create all database tables from SQLModel metadata."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency that provides a database session."""
    with Session(engine) as session:
        yield session
