from sqlalchemy import select
from sqlalchemy.orm import Session

from sparks.persistence.models.tool_execution import ToolExecution


class ToolExecutionRepository:
    """Persistence operations for ToolExecution records."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        task_id: int,
        tool_name: str,
        status: str,
        agent_run_id: int | None = None,
        arguments: str | None = None,
        result: str | None = None,
        latency_ms: float | None = None,
        risk_level: str | None = None,
        verification_result: str | None = None,
    ) -> ToolExecution:
        execution = ToolExecution(
            task_id=task_id,
            agent_run_id=agent_run_id,
            tool_name=tool_name,
            arguments=arguments,
            result=result,
            status=status,
            latency_ms=latency_ms,
            risk_level=risk_level,
            verification_result=verification_result,
        )

        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)

        return execution

    def get_by_id(self, execution_id: int) -> ToolExecution | None:
        return self.db.get(ToolExecution, execution_id)

    def list_by_task(self, task_id: int) -> list[ToolExecution]:
        statement = (
            select(ToolExecution)
            .where(ToolExecution.task_id == task_id)
            .order_by(ToolExecution.timestamp.asc(), ToolExecution.id.asc())
        )

        return list(self.db.scalars(statement).all())

    def list_by_agent_run(self, agent_run_id: int) -> list[ToolExecution]:
        statement = (
            select(ToolExecution)
            .where(ToolExecution.agent_run_id == agent_run_id)
            .order_by(ToolExecution.timestamp.asc(), ToolExecution.id.asc())
        )

        return list(self.db.scalars(statement).all())

    def update(self, execution: ToolExecution) -> ToolExecution:
        self.db.commit()
        self.db.refresh(execution)

        return execution

    def delete(self, execution: ToolExecution) -> None:
        self.db.delete(execution)
        self.db.commit()
