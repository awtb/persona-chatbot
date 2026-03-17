from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from persona_chatbot.common.exceptions import MemoryFactNotFound
from persona_chatbot.db.mappers.memory import apply_memory_fact_update_dto
from persona_chatbot.db.mappers.memory import to_memory_fact_dto
from persona_chatbot.db.models.memory_fact import MemoryFact
from persona_chatbot.db.repos.base import BaseRepository
from persona_chatbot.dto.base import PageDTO
from persona_chatbot.dto.memory import MemoryFactCreateDTO
from persona_chatbot.dto.memory import MemoryFactDTO
from persona_chatbot.dto.memory import MemoryFactUpdateDTO


class MemoryFactRepo(BaseRepository):
    async def get(
        self,
        memory_fact_id: UUID,
    ) -> MemoryFactDTO:
        query = select(MemoryFact).where(MemoryFact.id == memory_fact_id)
        memory_fact = await self._session.scalar(query)
        if memory_fact is None:
            raise MemoryFactNotFound(memory_fact_id=memory_fact_id)

        return to_memory_fact_dto(memory_fact)

    async def get_by_key(
        self,
        *,
        user_id: UUID,
        avatar_id: UUID,
        fact_key: str,
    ) -> MemoryFactDTO | None:
        query = select(MemoryFact).where(
            MemoryFact.user_id == user_id,
            MemoryFact.avatar_id == avatar_id,
            MemoryFact.fact_key == fact_key,
        )
        memory_fact = await self._session.scalar(query)
        if memory_fact is None:
            return None

        return to_memory_fact_dto(memory_fact)

    async def create(
        self,
        dto: MemoryFactCreateDTO,
    ) -> MemoryFactDTO:
        memory_fact = MemoryFact(
            user_id=dto.user_id,
            avatar_id=dto.avatar_id,
            fact_text=dto.fact_text,
            fact_key=dto.fact_key,
            source_chat_id=dto.source_chat_id,
        )
        self._session.add(memory_fact)
        await self._session.flush()

        return to_memory_fact_dto(memory_fact)

    async def upsert_many(
        self,
        dtos: list[MemoryFactCreateDTO],
    ) -> list[MemoryFactDTO]:
        if not dtos:
            return []

        values = [
            {
                "user_id": dto.user_id,
                "avatar_id": dto.avatar_id,
                "fact_text": dto.fact_text,
                "fact_key": dto.fact_key,
                "source_chat_id": dto.source_chat_id,
            }
            for dto in dtos
        ]
        stmt = insert(MemoryFact).values(values)
        stmt = stmt.on_conflict_do_update(
            constraint="uq_memory_facts_user_avatar_fact_key",
            set_={
                "fact_text": stmt.excluded.fact_text,
                "source_chat_id": stmt.excluded.source_chat_id,
            },
        )
        query = select(MemoryFact).from_statement(stmt.returning(MemoryFact))
        memory_facts = (await self._session.scalars(query)).all()
        await self._session.flush()

        items: list[MemoryFactDTO] = []
        for memory_fact in memory_facts:
            items.append(to_memory_fact_dto(memory_fact))
        return items

    async def update_fact(
        self,
        memory_fact_id: UUID,
        dto: MemoryFactUpdateDTO,
    ) -> MemoryFactDTO | None:
        query = select(MemoryFact).where(MemoryFact.id == memory_fact_id)
        memory_fact = await self._session.scalar(query)
        if memory_fact is None:
            return None

        apply_memory_fact_update_dto(
            memory_fact=memory_fact,
            dto=dto,
        )
        await self._session.flush()

        return to_memory_fact_dto(memory_fact)

    async def delete(
        self,
        memory_fact_id: UUID,
    ) -> bool:
        query = select(MemoryFact).where(MemoryFact.id == memory_fact_id)
        memory_fact = await self._session.scalar(query)
        if memory_fact is None:
            return False

        await self._session.delete(memory_fact)
        await self._session.flush()

        return True

    async def fetch_user_avatar_facts(
        self,
        *,
        user_id: UUID,
        avatar_id: UUID,
        limit: int = 100,
    ) -> list[MemoryFactDTO]:
        query = (
            select(MemoryFact)
            .where(
                MemoryFact.user_id == user_id,
                MemoryFact.avatar_id == avatar_id,
            )
            .order_by(MemoryFact.created_at.asc())
            .limit(limit)
        )
        memory_facts = (await self._session.scalars(query)).all()

        items: list[MemoryFactDTO] = []
        for memory_fact in memory_facts:
            items.append(to_memory_fact_dto(memory_fact))
        return items

    async def fetch_user_avatar_facts_page(
        self,
        *,
        user_id: UUID,
        avatar_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> PageDTO[MemoryFactDTO]:
        query = (
            select(MemoryFact)
            .where(
                MemoryFact.user_id == user_id,
                MemoryFact.avatar_id == avatar_id,
            )
            .order_by(MemoryFact.created_at.asc())
        )
        return await self._fetch(
            query=query,
            page=page,
            page_size=page_size,
            mapper_fn=to_memory_fact_dto,
        )
