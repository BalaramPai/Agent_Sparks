from datetime import datetime, timezone

from sparks.persistence.models.workflow_run import WorkflowRun, WorkflowRunStatus
from sparks.persistence.repositories.workflow_run import WorkflowRunRepository


class WorkflowRunService:
    def __init__(self, repository: WorkflowRunRepository):
        self.repository = repository

    def start_run(
        self,
        workflow_id: int,
        input: dict | None = None,
    ) -> WorkflowRun:
        workflow_run = self.repository.create(
            workflow_id=workflow_id,
            input=input,
        )

        workflow_run.status = WorkflowRunStatus.RUNNING
        workflow_run.started_at = datetime.now(timezone.utc)

        return self.repository.update(workflow_run)

    def get_run(self, workflow_run_id: int) -> WorkflowRun | None:
        return self.repository.get_by_id(workflow_run_id)

    def list_runs(self, workflow_id: int) -> list[WorkflowRun]:
        return self.repository.list_by_workflow(workflow_id)

    def complete_run(
        self,
        workflow_run: WorkflowRun,
        output: dict | None = None,
    ) -> WorkflowRun:
        workflow_run.status = WorkflowRunStatus.COMPLETED
        workflow_run.completed_at = datetime.now(timezone.utc)
        workflow_run.output = output

        return self.repository.update(workflow_run)

    def fail_run(
        self,
        workflow_run: WorkflowRun,
        error: str,
    ) -> WorkflowRun:
        workflow_run.status = WorkflowRunStatus.FAILED
        workflow_run.completed_at = datetime.now(timezone.utc)
        workflow_run.error = error

        return self.repository.update(workflow_run)

    def cancel_run(
        self,
        workflow_run: WorkflowRun,
    ) -> WorkflowRun:
        workflow_run.status = WorkflowRunStatus.CANCELLED
        workflow_run.completed_at = datetime.now(timezone.utc)

        return self.repository.update(workflow_run)

    def delete_run(self, workflow_run: WorkflowRun) -> None:
        self.repository.delete(workflow_run)
