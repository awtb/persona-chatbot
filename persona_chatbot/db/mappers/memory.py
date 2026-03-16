from persona_chatbot.db.models.memory_fact import MemoryFact
from persona_chatbot.dto.memory import MemoryFactDTO
from persona_chatbot.dto.memory import MemoryFactUpdateDTO


def to_memory_fact_dto(memory_fact: MemoryFact) -> MemoryFactDTO:
    return MemoryFactDTO(
        id=memory_fact.id,
        user_id=memory_fact.user_id,
        avatar_id=memory_fact.avatar_id,
        fact_text=memory_fact.fact_text,
        fact_key=memory_fact.fact_key,
        source_chat_id=memory_fact.source_chat_id,
        source_message_id=memory_fact.source_message_id,
        created_at=memory_fact.created_at,
    )


def apply_memory_fact_update_dto(
    memory_fact: MemoryFact,
    dto: MemoryFactUpdateDTO,
) -> None:
    memory_fact.user_id = dto.user_id
    memory_fact.avatar_id = dto.avatar_id
    memory_fact.fact_text = dto.fact_text
    memory_fact.fact_key = dto.fact_key
    memory_fact.source_chat_id = dto.source_chat_id
    memory_fact.source_message_id = dto.source_message_id
