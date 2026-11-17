from __future__ import annotations

from typing import Optional

from langchain_google_genai import ChatGoogleGenerativeAI

from .config import settings
from .models import ArchitectureGeneration


MAX_PROMPT_CHARS = 6000


class LLMClient:
    def __init__(self) -> None:
        self.enabled = settings.use_llm and bool(settings.api_key)
        self.client: Optional[ChatGoogleGenerativeAI] = None

        if self.enabled:
            self.client = ChatGoogleGenerativeAI(
                model=settings.model,
                api_key=settings.api_key,
                temperature=settings.temperature,
                request_timeout=60,
            )

    def generate(self, prompt: str) -> str:
        if not self.enabled or self.client is None:
            return self._fallback_response(prompt)

        short_prompt = prompt[:MAX_PROMPT_CHARS]
        try:
            response = self.client.invoke(short_prompt)
            return response.content if hasattr(response, "content") else str(response)
        except Exception as exc:
            print(f"[llm] Gemini call failed: {exc}")
            return self._fallback_response(prompt)

    def generate_structured(self, prompt: str) -> Optional[ArchitectureGeneration]:
        if not self.enabled or self.client is None:
            return None

        structured_client = self.client.with_structured_output(
            ArchitectureGeneration,
            method="json_schema",
        )
        return structured_client.invoke(prompt[:MAX_PROMPT_CHARS])

    def _fallback_response(self, prompt: str) -> str:
        return (
            "Gemini LLM is not configured or timed out in this environment. "
            "Using deterministic engineering workflow instead.\n"
            f"Prompt summary: {prompt[:200]}"
        )


llm_client = LLMClient()
