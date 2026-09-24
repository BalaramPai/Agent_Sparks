from sparks.persistence.database import SessionLocal
from sparks.persistence.repositories import SessionRepository
from sparks.persistence.models import User


def test_session_repository_create_get_and_end():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )

        db.add(user)
        db.flush()

        repository = SessionRepository(db)

        session = repository.create(
            user_id=user.id,
            device_info={
                "platform": "windows",
            },
            session_metadata={
                "source": "integration_test",
            },
        )

        assert session.id is not None
        assert session.user_id == user.id
        assert session.device_info == {
            "platform": "windows",
        }
        assert session.session_metadata == {
            "source": "integration_test",
        }
        assert session.ended_at is None

        db.commit()

        stored = repository.get_by_id(session.id)

        assert stored is not None
        assert stored.id == session.id
        assert stored.user_id == user.id

        repository.end_session(stored)

        assert stored.ended_at is not None

        db.commit()

        ended = repository.get_by_id(session.id)

        assert ended is not None
        assert ended.ended_at is not None

        repository.delete(ended)
        db.commit()

        assert repository.get_by_id(session.id) is None