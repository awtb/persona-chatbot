from collections.abc import AsyncIterator

import structlog
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionAssistantMessageParam
from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat import ChatCompletionSystemMessageParam
from openai.types.chat import ChatCompletionUserMessageParam

from persona_chatbot.common.enums import MessageRole
from persona_chatbot.dto.llm import LLMMessageDTO

logger = structlog.get_logger(__name__)


class LLMClient:
    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        timeout_sec: int,
    ) -> None:
        self._base_url = base_url
        self._model = model
        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout_sec,
        )

    def stream_reply(
        self,
        message: str,
        system_prompt: str,
        previous_messages: list[LLMMessageDTO],
    ) -> AsyncIterator[str]:
        return self._stream_reply(
            message=message,
            system_prompt=system_prompt,
            previous_messages=previous_messages,
        )

    async def _stream_reply(
        self,
        message: str,
        system_prompt: str,
        previous_messages: list[LLMMessageDTO],
    ) -> AsyncIterator[str]:
        has_deltas = False
        chunk_count = 0
        total_chars = 0
        messages = self._build_messages(
            message=message,
            system_prompt=system_prompt,
            previous_messages=previous_messages,
        )
        logger.debug(
            "Sending message to assistant",
            model=self._model,
            base_url=self._base_url,
            system_prompt=system_prompt,
            user_message=message,
            previous_messages_count=len(previous_messages),
            previous_messages=[
                {
                    "role": previous_message.role.value,
                    "content": previous_message.content,
                }
                for previous_message in previous_messages
            ],
            total_messages=len(messages),
        )
        stream = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            stream=True,
        )
        logger.debug(
            "Assistant stream started",
            model=self._model,
        )
        async for chunk in stream:
            if not chunk.choices:
                continue

            content = chunk.choices[0].delta.content
            if content:
                has_deltas = True
                chunk_count += 1
                chunk_offset_start = total_chars
                total_chars += len(content)
                logger.debug(
                    "Received assistant chunk",
                    model=self._model,
                    chunk_index=chunk_count,
                    chunk=content,
                    chunk_chars=len(content),
                    chunk_offset_start=chunk_offset_start,
                    chunk_offset_end=total_chars,
                    total_streamed_chars=total_chars,
                )
                yield content

        logger.debug(
            "Assistant stream finished",
            model=self._model,
            chunk_count=chunk_count,
            total_streamed_chars=total_chars,
            has_deltas=has_deltas,
        )
        if not has_deltas:
            logger.debug(
                "Assistant stream returned no deltas, using fallback",
                model=self._model,
            )
            yield "I could not generate a response."

    @staticmethod
    def _build_messages(
        message: str,
        system_prompt: str,
        previous_messages: list[LLMMessageDTO],
    ) -> list[ChatCompletionMessageParam]:
        messages: list[ChatCompletionMessageParam] = [
            ChatCompletionSystemMessageParam(
                role="system",
                content=system_prompt,
            ),
        ]
        messages.extend(
            LLMClient._to_openai_message(previous_message=previous_message)
            for previous_message in previous_messages
        )
        messages.append(
            ChatCompletionUserMessageParam(
                role="user",
                content=message,
            ),
        )

        return messages

    @staticmethod
    def _to_openai_message(
        previous_message: LLMMessageDTO,
    ) -> ChatCompletionMessageParam:
        if previous_message.role is MessageRole.USER:
            return ChatCompletionUserMessageParam(
                role="user",
                content=previous_message.content,
            )

        if previous_message.role is MessageRole.ASSISTANT:
            return ChatCompletionAssistantMessageParam(
                role="assistant",
                content=previous_message.content,
            )

        msg = f"Unsupported message role: {previous_message.role}"
        raise ValueError(msg)
