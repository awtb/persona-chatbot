from uuid import UUID

from persona_chatbot.common.exceptions.base import NotFoundError


class MemoryFactNotFound(NotFoundError):
    def __init__(
        self,
        memory_fact_id: UUID,
    ) -> None:
        super().__init__(
            f"Memory fact with id={memory_fact_id} was not found.",
        )
        self.memory_fact_id = memory_fact_id
