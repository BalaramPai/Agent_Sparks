from sparks.persistence.database import SessionLocal
from sparks.persistence.repositories.performance_metric import (
    PerformanceMetricRepository,
)


def test_create_metric():
    with SessionLocal() as db:
        repository = PerformanceMetricRepository(db)

        metric = repository.create(
            metric_type="model_latency",
            value=1250.5,
            unit="ms",
            component="inference",
            metadata={"model": "llama3.1:8b"},
        )

        assert metric.id is not None
        assert metric.metric_type == "model_latency"
        assert metric.value == 1250.5
        assert metric.unit == "ms"
        assert metric.component == "inference"
        assert metric.metric_metadata == {"model": "llama3.1:8b"}


def test_create_metric_without_metadata():
    with SessionLocal() as db:
        repository = PerformanceMetricRepository(db)

        metric = repository.create(
            metric_type="routing_latency",
            value=4.2,
            unit="ms",
            component="router",
        )

        assert metric.metric_metadata == {}


def test_get_metric():
    with SessionLocal() as db:
        repository = PerformanceMetricRepository(db)

        created = repository.create(
            metric_type="database_latency",
            value=12.0,
            unit="ms",
            component="postgres",
        )

        fetched = repository.get_by_id(created.id)

        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.metric_type == "database_latency"


def test_list_by_component():
    with SessionLocal() as db:
        repository = PerformanceMetricRepository(db)

        first = repository.create(
            metric_type="model_latency",
            value=1000.0,
            unit="ms",
            component="inference",
        )

        second = repository.create(
            metric_type="tokens_per_second",
            value=80.0,
            unit="tokens/sec",
            component="inference",
        )

        repository.create(
            metric_type="routing_latency",
            value=5.0,
            unit="ms",
            component="router",
        )

        metrics = repository.list_by_component("inference")
        metric_ids = [metric.id for metric in metrics]

        assert first.id in metric_ids
        assert second.id in metric_ids


def test_list_by_metric_type():
    with SessionLocal() as db:
        repository = PerformanceMetricRepository(db)

        first = repository.create(
            metric_type="model_latency",
            value=1000.0,
            unit="ms",
            component="inference",
        )

        second = repository.create(
            metric_type="model_latency",
            value=1200.0,
            unit="ms",
            component="inference",
        )

        repository.create(
            metric_type="routing_latency",
            value=5.0,
            unit="ms",
            component="router",
        )

        metrics = repository.list_by_metric_type("model_latency")
        metric_ids = [metric.id for metric in metrics]

        assert first.id in metric_ids
        assert second.id in metric_ids


def test_list_by_task():
    with SessionLocal() as db:
        repository = PerformanceMetricRepository(db)

        from sparks.persistence.models.task import Task
        from sparks.persistence.models.user import User

        user = User()
        db.add(user)
        db.commit()
        db.refresh(user)

        task = Task(
            user_id=user.id,
            goal="Performance test task",
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        metric = repository.create(
            metric_type="end_to_end_latency",
            value=2000.0,
            unit="ms",
            component="runtime",
            task_id=task.id,
        )

        metrics = repository.list_by_task(task.id)

        assert len(metrics) == 1
        assert metrics[0].id == metric.id


def test_update_metric():
    with SessionLocal() as db:
        repository = PerformanceMetricRepository(db)

        metric = repository.create(
            metric_type="tool_latency",
            value=50.0,
            unit="ms",
            component="tool",
        )

        metric.value = 75.0

        updated = repository.update(metric)

        assert updated.value == 75.0


def test_delete_metric():
    with SessionLocal() as db:
        repository = PerformanceMetricRepository(db)

        metric = repository.create(
            metric_type="network_latency",
            value=30.0,
            unit="ms",
            component="network",
        )

        metric_id = metric.id

        repository.delete(metric)

        assert repository.get_by_id(metric_id) is None
