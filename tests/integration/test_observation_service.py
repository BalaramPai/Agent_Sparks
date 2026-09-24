from sparks.persistence.database import SessionLocal
from sparks.persistence.models import Session as SessionModel
from sparks.persistence.models import User
from sparks.persistence.services import ObservationService


def test_observation_service_create_and_get():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )
        db.add(user)
        db.flush()

        service = ObservationService(db)

        observation = service.create_observation(
            user_id=user.id,
            event_type="terminal_error",
            content="Python import error appeared.",
            confidence=0.94,
            observation_metadata={
                "application": "Windows Terminal",
            },
        )

        service.commit()

        assert observation.id is not None

        loaded = service.get_observation(observation.id)

        assert loaded is not None
        assert loaded.id == observation.id
        assert loaded.user_id == user.id
        assert loaded.event_type == "terminal_error"
        assert loaded.content == "Python import error appeared."
        assert loaded.confidence == 0.94
        assert loaded.observation_metadata == {
            "application": "Windows Terminal",
        }


def test_observation_service_get_user_observations():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )
        db.add(user)
        db.flush()

        service = ObservationService(db)

        service.create_observation(
            user_id=user.id,
            event_type="application_active",
            content="VS Code became active.",
            confidence=0.98,
        )

        service.create_observation(
            user_id=user.id,
            event_type="terminal_error",
            content="Terminal error appeared.",
            confidence=0.91,
        )

        service.commit()

        observations = service.get_user_observations(user.id)

        assert len(observations) == 2
        assert observations[0].event_type == "application_active"
        assert observations[1].event_type == "terminal_error"


def test_observation_service_get_session_observations():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )
        db.add(user)
        db.flush()

        session = SessionModel(
            user_id=user.id,
            device_info={"platform": "windows"},
            session_metadata={"source": "integration_test"},
        )
        db.add(session)
        db.flush()

        service = ObservationService(db)

        service.create_observation(
            user_id=user.id,
            session_id=session.id,
            event_type="application_active",
            content="VS Code became active.",
            confidence=0.98,
        )

        service.create_observation(
            user_id=user.id,
            session_id=session.id,
            event_type="tool_executed",
            content="Diagnostic command executed.",
            confidence=0.99,
        )

        service.commit()

        observations = service.get_session_observations(session.id)

        assert len(observations) == 2
        assert observations[0].session_id == session.id
        assert observations[1].session_id == session.id


def test_observation_service_delete():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )
        db.add(user)
        db.flush()

        service = ObservationService(db)

        observation = service.create_observation(
            user_id=user.id,
            event_type="temporary",
            content="Temporary observation.",
            confidence=0.5,
        )

        service.commit()

        observation_id = observation.id

        service.delete_observation(observation)
        service.commit()

        assert service.get_observation(observation_id) is None


def test_observation_service_rollback():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )
        db.add(user)
        db.flush()

        service = ObservationService(db)

        service.create_observation(
            user_id=user.id,
            event_type="rollback_test",
            content="This should not persist.",
            confidence=0.5,
        )

        service.rollback()

        assert service.get_user_observations(user.id) == []
