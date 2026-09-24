from sqlalchemy import text

from sparks.persistence.database import SessionLocal


def test_database_connection():
    with SessionLocal() as db:
        result = db.execute(text("SELECT 1"))
        assert result.scalar() == 1
