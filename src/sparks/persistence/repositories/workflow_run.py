from sqlalchemy import select
from sqlalchemy.orm import Session

from sparks.persistence.models.workflow_run import WorkflowRun


class WorkflowRunRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        workflow_id: int,
        input: dict | None = None,
    ) -> WorkflowRun:
        workflow_run = WorkflowRun(
            workflow_id=workflow_id,
            input=input or {},
        )

        self.db.add(workflow_run)
        self.db.commit()
        self.db.refresh(workflow_run)

        return workflow_run

    def get_by_id(self, workflow_run_id: int) -> WorkflowRun | None:
        return self.db.get(WorkflowRun, workflow_run_id)

    def list_by_workflow(
        self,
        workflow_id: int,
    ) -> list[WorkflowRun]:
        statement = (
            select(WorkflowRun)
            .where(WorkflowRun.workflow_id == workflow_id)
            .order_by(
                WorkflowRun.started_at.asc().nulls_first(),
                WorkflowRun.id.asc(),
            )
        )

        return list(self.db.scalars(statement).all())

    def update(self, workflow_run: WorkflowRun) -> WorkflowRun:
        self.db.commit()
        self.db.refresh(workflow_run)

        return workflow_run

    def delete(self, workflow_run: WorkflowRun) -> None:
        self.db.delete(workflow_run)
        self.db.commit()
