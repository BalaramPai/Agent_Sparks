from sparks.persistence.models.agent_message import AgentMessage
from sparks.persistence.repositories.agent_message import AgentMessageRepository


class AgentMessageService:
    """Application-level operations for AgentMessage records."""

    def __init__(self, repository: AgentMessageRepository):
        self.repository = repository

    def send_message(
        self,
        task_id: int,
        sender: str,
        receiver: str,
        objective: str,
        context: str | None = None,
        requested_action: str | None = None,
        expected_result: str | None = None,
    ) -> AgentMessage:
        return self.repository.create(
            task_id=task_id,
            sender=sender,
            receiver=receiver,
            objective=objective,
            context=context,
            requested_action=requested_action,
            expected_result=expected_result,
        )

    def get_message(self, agent_message_id: int) -> AgentMessage | None:
        return self.repository.get_by_id(agent_message_id)

    def list_task_messages(self, task_id: int) -> list[AgentMessage]:
        return self.repository.list_by_task(task_id)

    def delete_message(self, agent_message: AgentMessage) -> None:
        self.repository.delete(agent_message)
