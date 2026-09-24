from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from sparks.config.settings import get_settings


settings = get_settings()


class Base(DeclarativeBase):
    """Base class for all SPARKS SQLAlchemy models."""

    pass


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)
def get_session():
    """Return a new database session."""

    return SessionLocal()

def get_db():
    """Provide a database session for application code."""

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
