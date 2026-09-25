from sparks.persistence.database import SessionLocal
from sparks.persistence.models.workflow import Workflow
from sparks.persistence.models.workflow_run import WorkflowRunStatus
from sparks.persistence.repositories.workflow_run import WorkflowRunRepository
from sparks.persistence.services.workflow_run import WorkflowRunService


def create_workflow(db):
    workflow = Workflow(
        name="Test Workflow",
        definition={"steps": [{"name": "step_one"}]},
    )
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    return workflow


def test_start_run():
    with SessionLocal() as db:
        workflow = create_workflow(db)
        service = WorkflowRunService(WorkflowRunRepository(db))

        run = service.start_run(
            workflow.id,
            {"input": "test"},
        )

        assert run.id is not None
        assert run.workflow_id == workflow.id
        assert run.status == WorkflowRunStatus.RUNNING
        assert run.started_at is not None
        assert run.input == {"input": "test"}


def test_get_run():
    with SessionLocal() as db:
        workflow = create_workflow(db)
        service = WorkflowRunService(WorkflowRunRepository(db))

        created = service.start_run(workflow.id)

        fetched = service.get_run(created.id)

        assert fetched is not None
        assert fetched.id == created.id


def test_list_runs():
    with SessionLocal() as db:
        workflow = create_workflow(db)
        service = WorkflowRunService(WorkflowRunRepository(db))

        first = service.start_run(workflow.id)
        second = service.start_run(workflow.id)

        runs = service.list_runs(workflow.id)
        run_ids = [run.id for run in runs]

        assert first.id in run_ids
        assert second.id in run_ids


def test_complete_run():
    with SessionLocal() as db:
        workflow = create_workflow(db)
        service = WorkflowRunService(WorkflowRunRepository(db))

        run = service.start_run(workflow.id)

        completed = service.complete_run(
            run,
            {"result": "success"},
        )

        assert completed.status == WorkflowRunStatus.COMPLETED
        assert completed.completed_at is not None
        assert completed.output == {"result": "success"}


def test_fail_run():
    with SessionLocal() as db:
        workflow = create_workflow(db)
        service = WorkflowRunService(WorkflowRunRepository(db))

        run = service.start_run(workflow.id)

        failed = service.fail_run(
            run,
            "Execution failed.",
        )

        assert failed.status == WorkflowRunStatus.FAILED
        assert failed.completed_at is not None
        assert failed.error == "Execution failed."


def test_cancel_run():
    with SessionLocal() as db:
        workflow = create_workflow(db)
        service = WorkflowRunService(WorkflowRunRepository(db))

        run = service.start_run(workflow.id)

        cancelled = service.cancel_run(run)

        assert cancelled.status == WorkflowRunStatus.CANCELLED
        assert cancelled.completed_at is not None


def test_delete_run():
    with SessionLocal() as db:
        workflow = create_workflow(db)
        service = WorkflowRunService(WorkflowRunRepository(db))

        run = service.start_run(workflow.id)
        run_id = run.id

        service.delete_run(run)

        assert service.get_run(run_id) is None
