from sparks.persistence.database import SessionLocal
from sparks.persistence.models import Session, User
from sparks.persistence.repositories import ContextSnapshotRepository


def test_context_snapshot_repository_create_and_get():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )

        db.add(user)
        db.flush()

        session = Session(
            user_id=user.id,
            device_info={"platform": "Windows"},
            session_metadata={"test": True},
        )

        db.add(session)
        db.flush()

        repository = ContextSnapshotRepository(db)

        snapshot = repository.create(
            session_id=session.id,
            active_application="VS Code",
            active_project="SPARKS",
            active_task="Phase 3",
            relevant_context="Implementing durable context persistence.",
            confidence=0.92,
            snapshot_metadata={"source": "test"},
        )

        db.commit()

        assert snapshot.id is not None
        assert snapshot.session_id == session.id
        assert snapshot.active_application == "VS Code"
        assert snapshot.active_project == "SPARKS"
        assert snapshot.active_task == "Phase 3"
        assert snapshot.relevant_context == "Implementing durable context persistence."
        assert snapshot.confidence == 0.92
        assert snapshot.snapshot_metadata == {"source": "test"}

        loaded_snapshot = repository.get_by_id(snapshot.id)

        assert loaded_snapshot is not None
        assert loaded_snapshot.id == snapshot.id
        assert loaded_snapshot.session_id == session.id


def test_context_snapshot_repository_list_by_session():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )

        db.add(user)
        db.flush()

        session = Session(
            user_id=user.id,
            device_info={"platform": "Windows"},
            session_metadata={},
        )

        db.add(session)
        db.flush()

        repository = ContextSnapshotRepository(db)

        first = repository.create(
            session_id=session.id,
            active_application="Chrome",
            confidence=0.80,
        )

        second = repository.create(
            session_id=session.id,
            active_application="VS Code",
            confidence=0.90,
        )

        db.commit()

        snapshots = repository.list_by_session(session.id)

        assert len(snapshots) == 2
        assert [snapshot.id for snapshot in snapshots] == [
            first.id,
            second.id,
        ]
        assert snapshots[0].active_application == "Chrome"
        assert snapshots[1].active_application == "VS Code"


def test_context_snapshot_repository_delete():
    with SessionLocal() as db:
        user = User(
            preferences={},
            settings={},
        )

        db.add(user)
        db.flush()

        session = Session(
            user_id=user.id,
            device_info={"platform": "Windows"},
            session_metadata={},
        )

        db.add(session)
        db.flush()

        repository = ContextSnapshotRepository(db)

        snapshot = repository.create(
            session_id=session.id,
            confidence=0.75,
        )

        db.commit()

        snapshot_id = snapshot.id

        repository.delete(snapshot)
        db.commit()

        assert repository.get_by_id(snapshot_id) is None
