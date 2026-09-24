from sqlalchemy import select
from sqlalchemy.orm import Session

from sparks.persistence.models.task import Task, TaskStatus


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        goal: str,
        priority: int = 0,
        status: TaskStatus = TaskStatus.PENDING,
        parent_task_id: int | None = None,
    ) -> Task:
        task = Task(
            user_id=user_id,
            parent_task_id=parent_task_id,
            goal=goal,
            status=status,
            priority=priority,
        )

        self.db.add(task)
        self.db.flush()

        return task

    def get_by_id(self, task_id: int) -> Task | None:
        statement = select(Task).where(Task.id == task_id)
        return self.db.scalar(statement)

    def list_by_user(self, user_id: int) -> list[Task]:
        statement = (
            select(Task)
            .where(Task.user_id == user_id)
            .order_by(Task.created_at, Task.id)
        )

        return list(self.db.scalars(statement).all())

    def list_by_status(
        self,
        status: TaskStatus,
    ) -> list[Task]:
        statement = (
            select(Task)
            .where(Task.status == status)
            .order_by(Task.created_at, Task.id)
        )

        return list(self.db.scalars(statement).all())

    def delete(self, task: Task) -> None:
        self.db.delete(task)
