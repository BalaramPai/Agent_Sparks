from sparks.persistence.database import SessionLocal
from sparks.persistence.models.workflow import Workflow
from sparks.persistence.models.workflow_run import WorkflowRun, WorkflowRunStatus
from sparks.persistence.repositories.workflow_run import WorkflowRunRepository


def create_workflow(db):
    workflow = Workflow(
        name="Test Workflow",
        description="Workflow run repository test.",
        definition={"steps": [{"name": "step_one"}]},
    )

    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    return workflow


def test_create_workflow_run():
    with SessionLocal() as db:
        workflow = create_workflow(db)
        repository = WorkflowRunRepository(db)

        workflow_run = repository.create(
            workflow_id=workflow.id,
            input={"value": 42},
        )

        assert workflow_run.id is not None
        assert workflow_run.workflow_id == workflow.id
        assert workflow_run.status == WorkflowRunStatus.PENDING
        assert workflow_run.input == {"value": 42}


def test_create_workflow_run_without_input():
    with SessionLocal() as db:
        workflow = create_workflow(db)
        repository = WorkflowRunRepository(db)

        workflow_run = repository.create(
            workflow_id=workflow.id,
        )

        assert workflow_run.input == {}


def test_get_workflow_run():
    with SessionLocal() as db:
        workflow = create_workflow(db)
        repository = WorkflowRunRepository(db)

        created = repository.create(
            workflow_id=workflow.id,
            input={"test": True},
        )

        fetched = repository.get_by_id(created.id)

        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.workflow_id == workflow.id


def test_list_workflow_runs():
    with SessionLocal() as db:
        workflow = create_workflow(db)
        repository = WorkflowRunRepository(db)

        first = repository.create(
            workflow_id=workflow.id,
            input={"run": 1},
        )

        second = repository.create(
            workflow_id=workflow.id,
            input={"run": 2},
        )

        runs = repository.list_by_workflow(workflow.id)

        run_ids = [run.id for run in runs]

        assert first.id in run_ids
        assert second.id in run_ids


def test_update_workflow_run():
    with SessionLocal() as db:
        workflow = create_workflow(db)
        repository = WorkflowRunRepository(db)

        workflow_run = repository.create(
            workflow_id=workflow.id,
        )

        workflow_run.status = WorkflowRunStatus.COMPLETED
        workflow_run.output = {"result": "success"}

        updated = repository.update(workflow_run)

        assert updated.status == WorkflowRunStatus.COMPLETED
        assert updated.output == {"result": "success"}


def test_delete_workflow_run():
    with SessionLocal() as db:
        workflow = create_workflow(db)
        repository = WorkflowRunRepository(db)

        workflow_run = repository.create(
            workflow_id=workflow.id,
        )

        workflow_run_id = workflow_run.id

        repository.delete(workflow_run)

        assert repository.get_by_id(workflow_run_id) is None
