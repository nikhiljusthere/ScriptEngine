"""An OpenAI-compatible LLM client.

ScriptEngine does not need a model to retrieve. This client exists for
summarisation and for scoring, and it speaks HTTP to whatever is already loaded
— Ollama, LM Studio, or anything else exposing the same shape.

The previous pipeline loaded Qwen2.5-7B in-process through `transformers`,
alongside the embedder and the reranker, all three competing for the same GPU
that ComfyUI needs to render. Talking to a server that already has a model
resident avoids paying for the weights twice.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from scriptengine.config import Settings, get_settings

logger = logging.getLogger(__name__)


class LLMUnavailable(RuntimeError):
    """No model endpoint answered. Callers should degrade, not crash."""


class LLMClient:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    @property
    def base_url(self) -> str:
        return self.settings.llm_base_url.rstrip("/")

    def available(self) -> bool:
        """Whether an endpoint is reachable. Never raises."""
        try:
            response = httpx.get(f"{self.base_url}/models", timeout=3.0)
            return response.status_code < 500
        except Exception:
            return False

    def models(self) -> list[str]:
        try:
            response = httpx.get(f"{self.base_url}/models", timeout=5.0)
            response.raise_for_status()
            return [item["id"] for item in response.json().get("data", [])]
        except Exception:
            return []

    def complete(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> str:
        messages: list[dict[str, Any]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            response = httpx.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.settings.llm_model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": False,
                },
                headers={"Authorization": f"Bearer {self.settings.llm_api_key}"},
                timeout=self.settings.llm_timeout_seconds,
            )
            response.raise_for_status()
        except Exception as error:
            raise LLMUnavailable(
                f"No response from {self.base_url} ({error}). "
                "Set SCRIPTENGINE_LLM_BASE_URL, or start Ollama or LM Studio."
            ) from error

        payload = response.json()
        try:
            return payload["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError) as error:
            raise LLMUnavailable(f"Unexpected response shape: {payload}") from error
