from sparks.persistence.database import SessionLocal
from sparks.persistence.models.agent_run import AgentRunStatus
from sparks.persistence.models.task import Task, TaskStatus
from sparks.persistence.models.user import User
from sparks.persistence.repositories.agent_run import AgentRunRepository
from sparks.persistence.repositories.tool_execution import ToolExecutionRepository
from sparks.persistence.services.tool_execution import ToolExecutionService


def create_test_task(db):
    user = User(
        preferences={},
        settings={},
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    task = Task(
        user_id=user.id,
        goal="Test ToolExecution service",
        status=TaskStatus.PENDING,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    return user, task


def create_test_agent_run(db, task_id):
    repository = AgentRunRepository(db)

    return repository.create(
        task_id=task_id,
        agent_type="executor",
        model="test-model",
        status=AgentRunStatus.RUNNING,
    )


def test_start_execution():
    with SessionLocal() as db:
        _, task = create_test_task(db)

        service = ToolExecutionService(ToolExecutionRepository(db))

        execution = service.start_execution(
            task_id=task.id,
            tool_name="test_tool",
            arguments='{"input": "test"}',
            risk_level="LOW",
        )

        assert execution.id is not None
        assert execution.task_id == task.id
        assert execution.tool_name == "test_tool"
        assert execution.arguments == '{"input": "test"}'
        assert execution.risk_level == "LOW"
        assert execution.status == "RUNNING"


def test_start_execution_with_agent_run():
    with SessionLocal() as db:
        _, task = create_test_task(db)
        agent_run = create_test_agent_run(db, task.id)

        service = ToolExecutionService(ToolExecutionRepository(db))

        execution = service.start_execution(
            task_id=task.id,
            tool_name="executor_tool",
            agent_run_id=agent_run.id,
        )

        assert execution.id is not None
        assert execution.agent_run_id == agent_run.id
        assert execution.status == "RUNNING"


def test_get_execution():
    with SessionLocal() as db:
        _, task = create_test_task(db)

        service = ToolExecutionService(ToolExecutionRepository(db))

        created = service.start_execution(
            task_id=task.id,
            tool_name="test_tool",
        )

        fetched = service.get_execution(created.id)

        assert fetched is not None
        assert fetched.id == created.id


def test_list_task_executions():
    with SessionLocal() as db:
        _, task = create_test_task(db)

        service = ToolExecutionService(ToolExecutionRepository(db))

        service.start_execution(
            task_id=task.id,
            tool_name="first_tool",
        )

        service.start_execution(
            task_id=task.id,
            tool_name="second_tool",
        )

        executions = service.list_task_executions(task.id)

        assert len(executions) == 2


def test_complete_execution():
    with SessionLocal() as db:
        _, task = create_test_task(db)

        service = ToolExecutionService(ToolExecutionRepository(db))

        execution = service.start_execution(
            task_id=task.id,
            tool_name="test_tool",
        )

        completed = service.complete_execution(
            execution,
            result="Tool completed successfully.",
            latency_ms=150.5,
            verification_result="VERIFIED",
        )

        assert completed.status == "COMPLETED"
        assert completed.result == "Tool completed successfully."
        assert completed.latency_ms == 150.5
        assert completed.verification_result == "VERIFIED"


def test_fail_execution():
    with SessionLocal() as db:
        _, task = create_test_task(db)

        service = ToolExecutionService(ToolExecutionRepository(db))

        execution = service.start_execution(
            task_id=task.id,
            tool_name="test_tool",
        )

        failed = service.fail_execution(
            execution,
            result="Tool execution failed.",
            latency_ms=200.0,
            verification_result="FAILED",
        )

        assert failed.status == "FAILED"
        assert failed.result == "Tool execution failed."
        assert failed.latency_ms == 200.0
        assert failed.verification_result == "FAILED"


def test_list_agent_run_executions():
    with SessionLocal() as db:
        _, task = create_test_task(db)
        agent_run = create_test_agent_run(db, task.id)

        service = ToolExecutionService(ToolExecutionRepository(db))

        execution_one = service.start_execution(
            task_id=task.id,
            tool_name="first_tool",
            agent_run_id=agent_run.id,
        )

        execution_two = service.start_execution(
            task_id=task.id,
            tool_name="second_tool",
            agent_run_id=agent_run.id,
        )

        executions = service.list_agent_run_executions(agent_run.id)

        execution_ids = [execution.id for execution in executions]

        assert execution_one.id in execution_ids
        assert execution_two.id in execution_ids
        assert len(executions) == 2


def test_delete_execution():
    with SessionLocal() as db:
        _, task = create_test_task(db)

        service = ToolExecutionService(ToolExecutionRepository(db))

        execution = service.start_execution(
            task_id=task.id,
            tool_name="test_tool",
        )

        execution_id = execution.id

        service.delete_execution(execution)

        assert service.get_execution(execution_id) is None
