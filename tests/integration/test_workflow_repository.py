from sparks.persistence.database import SessionLocal
from sparks.persistence.repositories.workflow import WorkflowRepository


def test_create_workflow():
    with SessionLocal() as db:
        repository = WorkflowRepository(db)

        workflow = repository.create(
            name="Test Workflow",
            description="Workflow persistence test.",
            definition={
                "steps": [
                    {"name": "step_one", "action": "test"},
                    {"name": "step_two", "action": "verify"},
                ]
            },
        )

        assert workflow.id is not None
        assert workflow.name == "Test Workflow"
        assert workflow.description == "Workflow persistence test."
        assert workflow.definition["steps"][0]["name"] == "step_one"
        assert workflow.created_at is not None
        assert workflow.updated_at is not None


def test_create_workflow_without_description():
    with SessionLocal() as db:
        repository = WorkflowRepository(db)

        workflow = repository.create(
            name="Minimal Workflow",
            definition={"steps": []},
        )

        assert workflow.id is not None
        assert workflow.description is None
        assert workflow.definition == {"steps": []}


def test_get_workflow_by_id():
    with SessionLocal() as db:
        repository = WorkflowRepository(db)

        created = repository.create(
            name="Fetch Workflow",
            definition={"steps": [{"name": "fetch"}]},
        )

        fetched = repository.get_by_id(created.id)

        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.name == "Fetch Workflow"


def test_list_all_workflows():
    with SessionLocal() as db:
        repository = WorkflowRepository(db)

        first = repository.create(
            name="First Workflow",
            definition={"steps": []},
        )

        second = repository.create(
            name="Second Workflow",
            definition={"steps": []},
        )

        workflows = repository.list_all()

        workflow_ids = [workflow.id for workflow in workflows]

        assert first.id in workflow_ids
        assert second.id in workflow_ids
        assert len(workflows) >= 2


def test_update_workflow():
    with SessionLocal() as db:
        repository = WorkflowRepository(db)

        workflow = repository.create(
            name="Original Workflow",
            description="Original description.",
            definition={"steps": []},
        )

        workflow.name = "Updated Workflow"
        workflow.description = "Updated description."
        workflow.definition = {
            "steps": [
                {"name": "new_step", "action": "execute"},
            ]
        }

        updated = repository.update(workflow)

        assert updated.name == "Updated Workflow"
        assert updated.description == "Updated description."
        assert updated.definition["steps"][0]["name"] == "new_step"


def test_delete_workflow():
    with SessionLocal() as db:
        repository = WorkflowRepository(db)

        workflow = repository.create(
            name="Delete Workflow",
            definition={"steps": []},
        )

        workflow_id = workflow.id

        repository.delete(workflow)

        assert repository.get_by_id(workflow_id) is None
