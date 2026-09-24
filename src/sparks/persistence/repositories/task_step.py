from sqlalchemy import select
from sqlalchemy.orm import Session

from sparks.persistence.models.task_step import TaskStep, TaskStepStatus


class TaskStepRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        task_id: int,
        step_order: int,
        description: str,
        status: TaskStepStatus = TaskStepStatus.PENDING,
    ) -> TaskStep:
        step = TaskStep(
            task_id=task_id,
            step_order=step_order,
            description=description,
            status=status,
        )

        self.db.add(step)
        self.db.flush()

        return step

    def get_by_id(self, step_id: int) -> TaskStep | None:
        statement = select(TaskStep).where(TaskStep.id == step_id)
        return self.db.scalar(statement)

    def list_by_task(self, task_id: int) -> list[TaskStep]:
        statement = (
            select(TaskStep)
            .where(TaskStep.task_id == task_id)
            .order_by(TaskStep.step_order, TaskStep.id)
        )

        return list(self.db.scalars(statement).all())

    def list_by_status(
        self,
        status: TaskStepStatus,
    ) -> list[TaskStep]:
        statement = (
            select(TaskStep)
            .where(TaskStep.status == status)
            .order_by(TaskStep.step_order, TaskStep.id)
        )

        return list(self.db.scalars(statement).all())

    def delete(self, step: TaskStep) -> None:
        self.db.delete(step)
