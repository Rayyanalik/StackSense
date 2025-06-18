from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.services.logging_service import LoggingService

logger = LoggingService()

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Enable connection health checks
    pool_size=5,  # Maximum number of connections to keep
    max_overflow=10,  # Maximum number of connections that can be created beyond pool_size
    echo=settings.SQL_ECHO  # Log SQL queries in development
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db():
    """
    Dependency for getting database session.
    Ensures session is closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(
            "Database session error",
            error=e,
            extra_data={"session_id": id(db)}
        )
        db.rollback()
        raise
    finally:
        db.close()

def init_db():
    """
    Initialize database by creating all tables.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(
            "Database initialization failed",
            error=e
        )
        raise 