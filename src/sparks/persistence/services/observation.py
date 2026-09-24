from sqlalchemy.orm import Session

from sparks.persistence.models import Observation
from sparks.persistence.repositories import ObservationRepository


class ObservationService:
    """Application service for durable SPARKS observations."""

    def __init__(self, db: Session):
        self.db = db
        self.observations = ObservationRepository(db)

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()

    def create_observation(
        self,
        user_id: int,
        event_type: str,
        content: str,
        confidence: float,
        session_id: int | None = None,
        observation_metadata: dict | None = None,
    ) -> Observation:
        return self.observations.create(
            user_id=user_id,
            session_id=session_id,
            event_type=event_type,
            content=content,
            confidence=confidence,
            observation_metadata=observation_metadata,
        )

    def get_observation(
        self,
        observation_id: int,
    ) -> Observation | None:
        return self.observations.get_by_id(observation_id)

    def get_user_observations(
        self,
        user_id: int,
    ) -> list[Observation]:
        return self.observations.list_by_user(user_id)

    def get_session_observations(
        self,
        session_id: int,
    ) -> list[Observation]:
        return self.observations.list_by_session(session_id)

    def delete_observation(
        self,
        observation: Observation,
    ) -> None:
        self.observations.delete(observation)
