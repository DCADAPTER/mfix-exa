from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LLMConfig:
    provider: str
    model: str


class LLMClient:
    def __init__(self, config: LLMConfig):
        self.config = config

    def generate(self, prompt: str) -> str:
        raise NotImplementedError
