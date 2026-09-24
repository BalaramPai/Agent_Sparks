from sqlalchemy import text

from sparks.persistence.database import engine


def check_database_connection() -> bool:
    """Return True when PostgreSQL is reachable and responsive."""

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
