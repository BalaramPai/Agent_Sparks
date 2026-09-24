from sparks.persistence.models.workflow import Workflow
from sparks.persistence.repositories.workflow import WorkflowRepository


class WorkflowService:
    """Application-level operations for Workflow records."""

    def __init__(self, repository: WorkflowRepository):
        self.repository = repository

    def create_workflow(
        self,
        name: str,
        definition: dict,
        description: str | None = None,
    ) -> Workflow:
        return self.repository.create(
            name=name,
            definition=definition,
            description=description,
        )

    def get_workflow(self, workflow_id: int) -> Workflow | None:
        return self.repository.get_by_id(workflow_id)

    def list_workflows(self) -> list[Workflow]:
        return self.repository.list_all()

    def update_workflow(
        self,
        workflow: Workflow,
        name: str | None = None,
        description: str | None = None,
        definition: dict | None = None,
    ) -> Workflow:
        if name is not None:
            workflow.name = name

        if description is not None:
            workflow.description = description

        if definition is not None:
            workflow.definition = definition

        return self.repository.update(workflow)

    def delete_workflow(self, workflow: Workflow) -> None:
        self.repository.delete(workflow)
