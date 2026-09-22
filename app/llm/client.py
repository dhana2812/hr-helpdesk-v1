import json
from collections.abc import AsyncGenerator
from typing import Any

import httpx

from app.config import settings
from app.llm.prompts import SYSTEM_PROMPT


class LLMResponseError(Exception):
    """Raised when the LLM response is missing or invalid."""


class LLMResponseStatusError(Exception):
    """Raised when the LLM response is not safe to process."""


class OpenRouterClient:
    def __init__(self) -> None:
        self.base_url = settings.openrouter_base_url
        self.api_key = settings.openrouter_api_key
        self.model = settings.openrouter_model

    @staticmethod
    def _response_format() -> dict:
        """
        Request a machine-readable JSON object from the model.

        The application still performs its own Pydantic validation after
        receiving the model response. This API-level constraint is an
        additional enforcement layer and does not replace schema validation.
        """
        return {
            "type": "json_object",
        }

    async def chat(
        self,
        user_message: str | None = None,
        system_prompt: str = SYSTEM_PROMPT,
        messages: list[dict] | None = None,
    ) -> dict:
        url = f"{self.base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        if messages is None:
            messages = [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_message or "",
                },
            ]
        else:
            messages = [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                *messages,
            ]

        payload = {
            "model": self.model,
            "messages": messages,
            "response_format": self._response_format(),
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                url,
                headers=headers,
                json=payload,
            )

        response.raise_for_status()

        return response.json()

    async def stream_chat(
        self,
        user_message: str | None = None,
        system_prompt: str = SYSTEM_PROMPT,
        messages: list[dict] | None = None,
    ) -> AsyncGenerator[dict, None]:
        """
        Stream assistant content from OpenRouter.

        Yields dictionaries containing either:

        {
            "type": "content",
            "content": "..."
        }

        or, after the model finishes:

        {
            "type": "status",
            "status": "success",
            "usage": {
                "input_tokens": 123,
                "output_tokens": 45,
            }
        }

        The final status is derived from the model's finish_reason.
        """

        url = f"{self.base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        if messages is None:
            messages = [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_message or "",
                },
            ]
        else:
            messages = [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                *messages,
            ]

        payload = {
            "model": self.model,
            "messages": messages,
            "response_format": self._response_format(),
            "stream": True,
            "stream_options": {
                "include_usage": True,
            },
        }

        final_status = "error"

        usage = {
            "input_tokens": 0,
            "output_tokens": 0,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                url,
                headers=headers,
                json=payload,
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if not line:
                        continue

                    if line == "data: [DONE]":
                        break

                    if not line.startswith("data: "):
                        continue

                    data = line[6:]

                    try:
                        chunk = json.loads(data)
                    except json.JSONDecodeError:
                        continue

                    usage_data = chunk.get("usage")

                    if isinstance(usage_data, dict):
                        usage["input_tokens"] = int(
                            usage_data.get("prompt_tokens", 0) or 0
                        )
                        usage["output_tokens"] = int(
                            usage_data.get("completion_tokens", 0) or 0
                        )

                    choices = chunk.get("choices", [])

                    # OpenRouter may send a final usage-only chunk.
                    if not choices:
                        continue

                    first_choice = choices[0]

                    if not isinstance(first_choice, dict):
                        final_status = "error"
                        continue

                    finish_reason = first_choice.get("finish_reason")

                    if finish_reason is not None:
                        final_status = self._status_from_finish_reason(
                            finish_reason
                        )

                    delta = first_choice.get("delta", {})

                    if not isinstance(delta, dict):
                        continue

                    content = self._normalize_stream_content(
                        delta.get("content")
                    )

                    if content:
                        yield {
                            "type": "content",
                            "content": content,
                        }

        yield {
            "type": "status",
            "status": final_status,
            "usage": usage,
        }

    @staticmethod
    def _normalize_stream_content(
        content: Any,
    ) -> str:
        """
        Normalize streamed model content into a string.

        OpenAI-compatible providers normally return a string, but some
        models/providers can return structured content such as a list
        of text parts or dictionaries. The application streaming layer
        requires strings so that chunks can safely be joined.
        """

        if content is None:
            return ""

        if isinstance(content, str):
            return content

        if isinstance(content, dict):
            text_value = content.get("text")

            if isinstance(text_value, str):
                return text_value

            nested_content = content.get("content")

            if isinstance(nested_content, str):
                return nested_content

            return ""

        if isinstance(content, list):
            parts: list[str] = []

            for item in content:
                if isinstance(item, str):
                    parts.append(item)
                    continue

                if isinstance(item, dict):
                    text_value = item.get("text")

                    if isinstance(text_value, str):
                        parts.append(text_value)
                        continue

                    nested_content = item.get("content")

                    if isinstance(nested_content, str):
                        parts.append(nested_content)

            return "".join(parts)

        return str(content)

    @staticmethod
    def _status_from_finish_reason(
        finish_reason: str | None,
    ) -> str:
        if finish_reason == "stop":
            return "success"

        if finish_reason in {
            "length",
            "max_tokens",
            "content_filter",
        }:
            return "incomplete"

        if finish_reason in {
            "cancelled",
            "canceled",
        }:
            return "cancelled"

        return "error"

    @staticmethod
    def check_response_status(response: dict) -> str:
        """
        Determine whether an LLM response is safe to process.

        Returns one of:
        - success
        - incomplete
        - cancelled
        - error
        """

        if not isinstance(response, dict):
            return "error"

        choices = response.get("choices")

        if not choices or not isinstance(choices, list):
            return "error"

        first_choice = choices[0]

        if not isinstance(first_choice, dict):
            return "error"

        finish_reason = first_choice.get("finish_reason")

        return OpenRouterClient._status_from_finish_reason(
            finish_reason
        )

    @classmethod
    def require_successful_response(
        cls,
        response: dict,
    ) -> str:
        """
        Check the LLM response status before the application uses it.

        Raises LLMResponseStatusError unless the response completed normally.
        """

        status = cls.check_response_status(response)

        if status != "success":
            raise LLMResponseStatusError(
                f"LLM response status is '{status}'. "
                "The response must not be processed or shown."
            )

        return status

    @staticmethod
    def extract_content(response: dict) -> str:
        choices = response.get("choices", [])

        if not choices:
            raise LLMResponseError(
                "LLM response contains no choices."
            )

        message = choices[0].get("message", {})
        content = message.get("content")

        if not content:
            raise LLMResponseError(
                "LLM response contains no message content."
            )

        normalized_content = OpenRouterClient._normalize_stream_content(
            content
        )

        if not normalized_content:
            raise LLMResponseError(
                "LLM response contains no usable message content."
            )

        return normalized_content

    @staticmethod
    def extract_usage(response: dict) -> dict:
        usage = response.get("usage", {})

        return {
            "input_tokens": usage.get("prompt_tokens", 0),
            "output_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
        }


llm_client = OpenRouterClient()