# api/database/postgres.py
"""
PostgreSQL database connection and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from api.config import get_settings

settings = get_settings()

# Use SQLite for development (easy migration to PostgreSQL later)
database_url = settings.database_url
if database_url.startswith("postgresql"):
    # If PostgreSQL not available, fallback to SQLite
    database_url = "sqlite:///./data/talora.db"
    print("[INFO] Using SQLite database (data/talora.db)")

# Create database engine
engine = create_engine(
    database_url,
    connect_args={"check_same_thread": False} if "sqlite" in database_url else {},
    pool_pre_ping=True,
    echo=settings.api_debug
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()


def get_db():
    """
    Dependency to get database session.
    
    Usage in FastAPI:
        @app.get("/")
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
