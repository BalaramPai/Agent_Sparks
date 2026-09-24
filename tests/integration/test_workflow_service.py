from sparks.persistence.database import SessionLocal
from sparks.persistence.repositories.workflow import WorkflowRepository
from sparks.persistence.services.workflow import WorkflowService


def test_create_workflow():
    with SessionLocal() as db:
        service = WorkflowService(WorkflowRepository(db))

        workflow = service.create_workflow(
            name="Test Workflow",
            description="Service test workflow.",
            definition={
                "steps": [
                    {"name": "step_one", "action": "execute"},
                ]
            },
        )

        assert workflow.id is not None
        assert workflow.name == "Test Workflow"
        assert workflow.description == "Service test workflow."
        assert workflow.definition["steps"][0]["name"] == "step_one"


def test_get_workflow():
    with SessionLocal() as db:
        service = WorkflowService(WorkflowRepository(db))

        created = service.create_workflow(
            name="Fetch Workflow",
            definition={"steps": []},
        )

        fetched = service.get_workflow(created.id)

        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.name == "Fetch Workflow"


def test_list_workflows():
    with SessionLocal() as db:
        service = WorkflowService(WorkflowRepository(db))

        first = service.create_workflow(
            name="First Workflow",
            definition={"steps": []},
        )

        second = service.create_workflow(
            name="Second Workflow",
            definition={"steps": []},
        )

        workflows = service.list_workflows()

        workflow_ids = [workflow.id for workflow in workflows]

        assert first.id in workflow_ids
        assert second.id in workflow_ids


def test_update_workflow():
    with SessionLocal() as db:
        service = WorkflowService(WorkflowRepository(db))

        workflow = service.create_workflow(
            name="Original Workflow",
            description="Original description.",
            definition={"steps": []},
        )

        updated = service.update_workflow(
            workflow,
            name="Updated Workflow",
            description="Updated description.",
            definition={
                "steps": [
                    {"name": "new_step", "action": "execute"},
                ]
            },
        )

        assert updated.name == "Updated Workflow"
        assert updated.description == "Updated description."
        assert updated.definition["steps"][0]["name"] == "new_step"


def test_update_workflow_partial():
    with SessionLocal() as db:
        service = WorkflowService(WorkflowRepository(db))

        workflow = service.create_workflow(
            name="Original Workflow",
            description="Keep this description.",
            definition={"steps": [{"name": "original"}]},
        )

        updated = service.update_workflow(
            workflow,
            name="Updated Workflow",
        )

        assert updated.name == "Updated Workflow"
        assert updated.description == "Keep this description."
        assert updated.definition == {"steps": [{"name": "original"}]}


def test_delete_workflow():
    with SessionLocal() as db:
        service = WorkflowService(WorkflowRepository(db))

        workflow = service.create_workflow(
            name="Delete Workflow",
            definition={"steps": []},
        )

        workflow_id = workflow.id

        service.delete_workflow(workflow)

        assert service.get_workflow(workflow_id) is None
