from sqlalchemy import select
from sqlalchemy.orm import Session

from sparks.persistence.models.context_snapshot import ContextSnapshot


class ContextSnapshotRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        session_id: int,
        confidence: float,
        active_application: str | None = None,
        active_project: str | None = None,
        active_task: str | None = None,
        relevant_context: str | None = None,
        snapshot_metadata: dict | None = None,
    ) -> ContextSnapshot:
        snapshot = ContextSnapshot(
            session_id=session_id,
            active_application=active_application,
            active_project=active_project,
            active_task=active_task,
            relevant_context=relevant_context,
            confidence=confidence,
            snapshot_metadata=snapshot_metadata or {},
        )

        self.db.add(snapshot)
        self.db.flush()

        return snapshot

    def get_by_id(self, snapshot_id: int) -> ContextSnapshot | None:
        statement = select(ContextSnapshot).where(
            ContextSnapshot.id == snapshot_id
        )
        return self.db.scalar(statement)

    def list_by_session(self, session_id: int) -> list[ContextSnapshot]:
        statement = (
            select(ContextSnapshot)
            .where(ContextSnapshot.session_id == session_id)
            .order_by(ContextSnapshot.timestamp, ContextSnapshot.id)
        )

        return list(self.db.scalars(statement).all())

    def delete(self, snapshot: ContextSnapshot) -> None:
        self.db.delete(snapshot)
