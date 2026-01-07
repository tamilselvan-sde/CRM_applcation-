import logging
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

engine = create_engine(
    settings.postgres_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    logger.info("Initializing PostgreSQL database...")
    Base.metadata.create_all(bind=engine)
    logger.info("PostgreSQL database initialized successfully")
