from sqlalchemy import select
from sqlalchemy.orm import Session

from sparks.persistence.models.model_run import ModelRun


class ModelRunRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        model: str,
        provider: str,
        request_type: str,
        success: bool,
        task_id: int | None = None,
        token_count: int | None = None,
        ttft_ms: float | None = None,
        total_latency_ms: float | None = None,
        tokens_per_second: float | None = None,
        vram_mb: float | None = None,
        cpu_percent: float | None = None,
        ram_mb: float | None = None,
        task_type: str | None = None,
    ) -> ModelRun:
        model_run = ModelRun(
            task_id=task_id,
            model=model,
            provider=provider,
            request_type=request_type,
            token_count=token_count,
            ttft_ms=ttft_ms,
            total_latency_ms=total_latency_ms,
            tokens_per_second=tokens_per_second,
            vram_mb=vram_mb,
            cpu_percent=cpu_percent,
            ram_mb=ram_mb,
            task_type=task_type,
            success=success,
        )

        self.db.add(model_run)
        self.db.commit()
        self.db.refresh(model_run)

        return model_run

    def get_by_id(self, model_run_id: int) -> ModelRun | None:
        return self.db.get(ModelRun, model_run_id)

    def list_by_task(self, task_id: int) -> list[ModelRun]:
        statement = (
            select(ModelRun)
            .where(ModelRun.task_id == task_id)
            .order_by(ModelRun.created_at.asc(), ModelRun.id.asc())
        )

        return list(self.db.scalars(statement).all())

    def list_by_model(self, model: str) -> list[ModelRun]:
        statement = (
            select(ModelRun)
            .where(ModelRun.model == model)
            .order_by(ModelRun.created_at.asc(), ModelRun.id.asc())
        )

        return list(self.db.scalars(statement).all())

    def update(self, model_run: ModelRun) -> ModelRun:
        self.db.commit()
        self.db.refresh(model_run)

        return model_run

    def delete(self, model_run: ModelRun) -> None:
        self.db.delete(model_run)
        self.db.commit()
