from sparks.persistence.database import SessionLocal
from sparks.persistence.models.model_run import ModelRun
from sparks.persistence.repositories.model_run import ModelRunRepository
from sparks.persistence.services.model_run import ModelRunService


def test_record_run():
    with SessionLocal() as db:
        service = ModelRunService(ModelRunRepository(db))

        model_run = service.record_run(
            model="llama3.1:8b",
            provider="ollama",
            request_type="general",
            success=True,
            token_count=256,
            ttft_ms=150.0,
            total_latency_ms=2200.0,
            tokens_per_second=116.4,
            vram_mb=3200.0,
            cpu_percent=35.0,
            ram_mb=7600.0,
            task_type="general",
        )

        assert model_run.id is not None
        assert model_run.model == "llama3.1:8b"
        assert model_run.provider == "ollama"
        assert model_run.success is True
        assert model_run.token_count == 256


def test_get_run():
    with SessionLocal() as db:
        service = ModelRunService(ModelRunRepository(db))

        created = service.record_run(
            model="test-model",
            provider="ollama",
            request_type="general",
            success=True,
        )

        fetched = service.get_run(created.id)

        assert fetched is not None
        assert fetched.id == created.id


def test_list_by_task():
    with SessionLocal() as db:
        service = ModelRunService(ModelRunRepository(db))

        from sparks.persistence.models.task import Task
        from sparks.persistence.models.user import User

        user = User()
        db.add(user)
        db.commit()
        db.refresh(user)

        task = Task(
            user_id=user.id,
            goal="Model execution task",
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        first = service.record_run(
            model="model-a",
            provider="ollama",
            request_type="general",
            success=True,
            task_id=task.id,
        )

        second = service.record_run(
            model="model-b",
            provider="ollama",
            request_type="reasoning",
            success=True,
            task_id=task.id,
        )

        runs = service.list_by_task(task.id)
        run_ids = [run.id for run in runs]

        assert first.id in run_ids
        assert second.id in run_ids


def test_list_by_model():
    with SessionLocal() as db:
        service = ModelRunService(ModelRunRepository(db))

        first = service.record_run(
            model="llama3.1:8b",
            provider="ollama",
            request_type="general",
            success=True,
        )

        second = service.record_run(
            model="llama3.1:8b",
            provider="ollama",
            request_type="reasoning",
            success=True,
        )

        runs = service.list_by_model("llama3.1:8b")
        run_ids = [run.id for run in runs]

        assert first.id in run_ids
        assert second.id in run_ids


def test_update_run():
    with SessionLocal() as db:
        service = ModelRunService(ModelRunRepository(db))

        model_run = service.record_run(
            model="test-model",
            provider="ollama",
            request_type="general",
            success=False,
        )

        model_run.success = True
        model_run.total_latency_ms = 1500.0

        updated = service.update_run(model_run)

        assert updated.success is True
        assert updated.total_latency_ms == 1500.0


def test_delete_run():
    with SessionLocal() as db:
        service = ModelRunService(ModelRunRepository(db))

        model_run = service.record_run(
            model="test-model",
            provider="ollama",
            request_type="general",
            success=True,
        )

        model_run_id = model_run.id

        service.delete_run(model_run)

        assert service.get_run(model_run_id) is None
