"""
Database configuration and session management for the sensors server.
"""
from sqlmodel import SQLModel, create_engine, Session
from typing import Generator

# Database URL - using SQLite for development
DATABASE_URL = "sqlite:///./external/sensors.db"

# Create engine
engine = create_engine(
    DATABASE_URL, 
    echo=False,  # Set to True for SQL query logging
    connect_args={"check_same_thread": False}  # Required for SQLite
)

def create_db_and_tables():
    """Create database tables if they don't exist."""
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """Dependency to get database session."""
    with Session(engine) as session:
        yield session 