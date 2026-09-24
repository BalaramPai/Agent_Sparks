from sparks.persistence.database import SessionLocal
from sparks.persistence.models import Session as SessionModel
from sparks.persistence.models import User
from sparks.persistence.repositories import ObservationRepository


def test_observation_repository_create_and_get():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )
        db.add(user)
        db.flush()

        repository = ObservationRepository(db)

        observation = repository.create(
            user_id=user.id,
            event_type="terminal_error",
            content="Python import error appeared.",
            confidence=0.94,
            observation_metadata={
                "application": "Windows Terminal",
            },
        )

        db.commit()

        assert observation.id is not None
        assert observation.user_id == user.id
        assert observation.session_id is None
        assert observation.event_type == "terminal_error"
        assert observation.content == "Python import error appeared."
        assert observation.confidence == 0.94
        assert observation.observation_metadata == {
            "application": "Windows Terminal",
        }

        loaded = repository.get_by_id(observation.id)

        assert loaded is not None
        assert loaded.id == observation.id
        assert loaded.content == "Python import error appeared."


def test_observation_repository_list_by_user():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )
        db.add(user)
        db.flush()

        repository = ObservationRepository(db)

        repository.create(
            user_id=user.id,
            event_type="application_active",
            content="VS Code became active.",
            confidence=0.98,
        )

        repository.create(
            user_id=user.id,
            event_type="terminal_error",
            content="Terminal error appeared.",
            confidence=0.91,
        )

        db.commit()

        observations = repository.list_by_user(user.id)

        assert len(observations) == 2
        assert observations[0].event_type == "application_active"
        assert observations[1].event_type == "terminal_error"


def test_observation_repository_list_by_session():
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

        repository = ObservationRepository(db)

        repository.create(
            user_id=user.id,
            session_id=session.id,
            event_type="application_active",
            content="VS Code became active.",
            confidence=0.98,
        )

        repository.create(
            user_id=user.id,
            session_id=session.id,
            event_type="tool_executed",
            content="A diagnostic command was executed.",
            confidence=0.99,
        )

        db.commit()

        observations = repository.list_by_session(session.id)

        assert len(observations) == 2
        assert observations[0].session_id == session.id
        assert observations[1].session_id == session.id
        assert observations[0].event_type == "application_active"
        assert observations[1].event_type == "tool_executed"


def test_observation_repository_delete():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )
        db.add(user)
        db.flush()

        repository = ObservationRepository(db)

        observation = repository.create(
            user_id=user.id,
            event_type="temporary",
            content="Temporary observation.",
            confidence=0.5,
        )

        db.commit()

        observation_id = observation.id

        repository.delete(observation)
        db.commit()

        assert repository.get_by_id(observation_id) is None
