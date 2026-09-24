from sqlalchemy import select
from sqlalchemy.orm import Session

from sparks.persistence.models.workflow import Workflow


class WorkflowRepository:
    """Persistence operations for Workflow records."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        name: str,
        definition: dict,
        description: str | None = None,
    ) -> Workflow:
        workflow = Workflow(
            name=name,
            description=description,
            definition=definition,
        )

        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)

        return workflow

    def get_by_id(self, workflow_id: int) -> Workflow | None:
        return self.db.get(Workflow, workflow_id)

    def list_all(self) -> list[Workflow]:
        statement = (
            select(Workflow)
            .order_by(Workflow.created_at.asc(), Workflow.id.asc())
        )

        return list(self.db.scalars(statement).all())

    def update(self, workflow: Workflow) -> Workflow:
        self.db.commit()
        self.db.refresh(workflow)

        return workflow

    def delete(self, workflow: Workflow) -> None:
        self.db.delete(workflow)
        self.db.commit()
