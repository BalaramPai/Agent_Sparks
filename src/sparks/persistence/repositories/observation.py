from sqlalchemy import select
from sqlalchemy.orm import Session

from sparks.persistence.models import Observation


class ObservationRepository:
    """Persistence operations for durable SPARKS observations."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        event_type: str,
        content: str,
        confidence: float,
        session_id: int | None = None,
        observation_metadata: dict | None = None,
    ) -> Observation:
        observation = Observation(
            user_id=user_id,
            session_id=session_id,
            event_type=event_type,
            content=content,
            confidence=confidence,
            observation_metadata=observation_metadata or {},
        )

        self.db.add(observation)
        self.db.flush()

        return observation

    def get_by_id(self, observation_id: int) -> Observation | None:
        statement = select(Observation).where(
            Observation.id == observation_id
        )

        return self.db.scalar(statement)

    def list_by_user(self, user_id: int) -> list[Observation]:
        statement = (
            select(Observation)
            .where(Observation.user_id == user_id)
            .order_by(Observation.timestamp, Observation.id)
        )

        return list(self.db.scalars(statement).all())

    def list_by_session(self, session_id: int) -> list[Observation]:
        statement = (
            select(Observation)
            .where(Observation.session_id == session_id)
            .order_by(Observation.timestamp, Observation.id)
        )

        return list(self.db.scalars(statement).all())

    def delete(self, observation: Observation) -> None:
        self.db.delete(observation)
