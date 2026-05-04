from __future__ import annotations

from src.agent.llm.base import LLMClient


class MockLLMClient(LLMClient):
    def generate(self, prompt: str) -> str:
        # Deterministic placeholder for local tests/dev.
        return f"[mock:{self.config.model}] {prompt[:120]}"
