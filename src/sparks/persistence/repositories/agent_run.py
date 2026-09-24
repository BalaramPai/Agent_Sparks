from sqlalchemy import select
from sqlalchemy.orm import Session

from sparks.persistence.models.agent_run import AgentRun, AgentRunStatus


class AgentRunRepository:
    """Persistence operations for AgentRun records."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        task_id: int,
        agent_type: str,
        model: str,
        status: AgentRunStatus = AgentRunStatus.RUNNING,
    ) -> AgentRun:
        agent_run = AgentRun(
            task_id=task_id,
            agent_type=agent_type,
            model=model,
            status=status,
        )

        self.db.add(agent_run)
        self.db.commit()
        self.db.refresh(agent_run)

        return agent_run

    def get_by_id(self, agent_run_id: int) -> AgentRun | None:
        return self.db.get(AgentRun, agent_run_id)

    def list_by_task(self, task_id: int) -> list[AgentRun]:
        statement = (
            select(AgentRun)
            .where(AgentRun.task_id == task_id)
            .order_by(AgentRun.started_at.asc(), AgentRun.id.asc())
        )

        return list(self.db.scalars(statement).all())

    def update(self, agent_run: AgentRun) -> AgentRun:
        self.db.commit()
        self.db.refresh(agent_run)

        return agent_run

    def delete(self, agent_run: AgentRun) -> None:
        self.db.delete(agent_run)
        self.db.commit()
