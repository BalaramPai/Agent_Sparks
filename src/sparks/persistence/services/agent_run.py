from sparks.persistence.models.agent_run import AgentRun, AgentRunStatus
from sparks.persistence.repositories.agent_run import AgentRunRepository


class AgentRunService:
    """Application-level operations for AgentRun records."""

    def __init__(self, repository: AgentRunRepository):
        self.repository = repository

    def start_run(
        self,
        task_id: int,
        agent_type: str,
        model: str,
    ) -> AgentRun:
        return self.repository.create(
            task_id=task_id,
            agent_type=agent_type,
            model=model,
            status=AgentRunStatus.RUNNING,
        )

    def get_run(self, agent_run_id: int) -> AgentRun | None:
        return self.repository.get_by_id(agent_run_id)

    def list_task_runs(self, task_id: int) -> list[AgentRun]:
        return self.repository.list_by_task(task_id)

    def complete_run(
        self,
        agent_run: AgentRun,
        result: str | None = None,
        tokens: int | None = None,
        latency: float | None = None,
    ) -> AgentRun:
        agent_run.status = AgentRunStatus.COMPLETED
        agent_run.result = result
        agent_run.tokens = tokens
        agent_run.latency = latency

        return self.repository.update(agent_run)

    def fail_run(
        self,
        agent_run: AgentRun,
        error: str,
        latency: float | None = None,
    ) -> AgentRun:
        agent_run.status = AgentRunStatus.FAILED
        agent_run.error = error
        agent_run.latency = latency

        return self.repository.update(agent_run)

    def cancel_run(self, agent_run: AgentRun) -> AgentRun:
        agent_run.status = AgentRunStatus.CANCELLED

        return self.repository.update(agent_run)
