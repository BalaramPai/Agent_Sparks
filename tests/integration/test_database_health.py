from sparks.persistence.health import check_database_connection


def test_database_health():
    assert check_database_connection() is True
