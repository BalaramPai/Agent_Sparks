from sparks.persistence.database import SessionLocal
from sparks.persistence.models import User
from sparks.persistence.services import SessionService


def test_session_service_lifecycle():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )

        db.add(user)
        db.flush()

        service = SessionService(db)

        session = service.create_session(
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
        assert session.ended_at is None

        service.commit()

        stored = service.get_session(session.id)

        assert stored is not None
        assert stored.id == session.id
        assert stored.user_id == user.id

        service.end_session(stored)

        assert stored.ended_at is not None

        service.commit()

        ended = service.get_session(session.id)

        assert ended is not None
        assert ended.ended_at is not None

        service.delete_session(ended)
        service.commit()

        assert service.get_session(session.id) is None