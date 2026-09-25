from sqlalchemy import select
from sqlalchemy.orm import Session

from sparks.persistence.models.performance_metric import PerformanceMetric


class PerformanceMetricRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        metric_type: str,
        value: float,
        unit: str,
        component: str,
        task_id: int | None = None,
        model_run_id: int | None = None,
        metadata: dict | None = None,
    ) -> PerformanceMetric:
        metric = PerformanceMetric(
            metric_type=metric_type,
            value=value,
            unit=unit,
            component=component,
            task_id=task_id,
            model_run_id=model_run_id,
            metric_metadata=metadata or {},
        )

        self.db.add(metric)
        self.db.commit()
        self.db.refresh(metric)

        return metric

    def get_by_id(self, metric_id: int) -> PerformanceMetric | None:
        return self.db.get(PerformanceMetric, metric_id)

    def list_by_component(
        self,
        component: str,
    ) -> list[PerformanceMetric]:
        statement = (
            select(PerformanceMetric)
            .where(PerformanceMetric.component == component)
            .order_by(
                PerformanceMetric.recorded_at.asc(),
                PerformanceMetric.id.asc(),
            )
        )

        return list(self.db.scalars(statement).all())

    def list_by_metric_type(
        self,
        metric_type: str,
    ) -> list[PerformanceMetric]:
        statement = (
            select(PerformanceMetric)
            .where(PerformanceMetric.metric_type == metric_type)
            .order_by(
                PerformanceMetric.recorded_at.asc(),
                PerformanceMetric.id.asc(),
            )
        )

        return list(self.db.scalars(statement).all())

    def list_by_task(
        self,
        task_id: int,
    ) -> list[PerformanceMetric]:
        statement = (
            select(PerformanceMetric)
            .where(PerformanceMetric.task_id == task_id)
            .order_by(
                PerformanceMetric.recorded_at.asc(),
                PerformanceMetric.id.asc(),
            )
        )

        return list(self.db.scalars(statement).all())

    def update(
        self,
        metric: PerformanceMetric,
    ) -> PerformanceMetric:
        self.db.commit()
        self.db.refresh(metric)

        return metric

    def delete(self, metric: PerformanceMetric) -> None:
        self.db.delete(metric)
        self.db.commit()
