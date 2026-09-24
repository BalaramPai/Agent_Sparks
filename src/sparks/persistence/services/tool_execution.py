from sparks.persistence.models.tool_execution import ToolExecution
from sparks.persistence.repositories.tool_execution import ToolExecutionRepository


class ToolExecutionService:
    """Application-level operations for ToolExecution records."""

    def __init__(self, repository: ToolExecutionRepository):
        self.repository = repository

    def start_execution(
        self,
        task_id: int,
        tool_name: str,
        agent_run_id: int | None = None,
        arguments: str | None = None,
        risk_level: str | None = None,
    ) -> ToolExecution:
        return self.repository.create(
            task_id=task_id,
            agent_run_id=agent_run_id,
            tool_name=tool_name,
            arguments=arguments,
            status="RUNNING",
            risk_level=risk_level,
        )

    def get_execution(self, execution_id: int) -> ToolExecution | None:
        return self.repository.get_by_id(execution_id)

    def list_task_executions(self, task_id: int) -> list[ToolExecution]:
        return self.repository.list_by_task(task_id)

    def list_agent_run_executions(
        self,
        agent_run_id: int,
    ) -> list[ToolExecution]:
        return self.repository.list_by_agent_run(agent_run_id)

    def complete_execution(
        self,
        execution: ToolExecution,
        result: str | None = None,
        latency_ms: float | None = None,
        verification_result: str | None = None,
    ) -> ToolExecution:
        execution.status = "COMPLETED"
        execution.result = result
        execution.latency_ms = latency_ms
        execution.verification_result = verification_result

        return self.repository.update(execution)

    def fail_execution(
        self,
        execution: ToolExecution,
        result: str | None = None,
        latency_ms: float | None = None,
        verification_result: str | None = None,
    ) -> ToolExecution:
        execution.status = "FAILED"
        execution.result = result
        execution.latency_ms = latency_ms
        execution.verification_result = verification_result

        return self.repository.update(execution)

    def delete_execution(self, execution: ToolExecution) -> None:
        self.repository.delete(execution)
