from __future__ import annotations

from src.agent.llm.base import LLMClient
from src.agent.two_stage.types import AnalyzerInsight, IterationState


class AnalyzerAgent:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def analyze(self, state: IterationState) -> AnalyzerInsight:
        prompt = (
            "Analyze previous run.\n"
            f"status={state.last_status}\n"
            f"input={state.last_input}\n"
            f"stdout={state.last_stdout}\n"
            "Return concise failure insight and guardrails."
        )
        raw = self.llm.generate(prompt)
        causes = ["divergence risk" if state.last_status != "ok" else "improve objective near current x"]
        guardrails = ["limit step size", "keep x in [-5, 5]"]
        return AnalyzerInsight(summary=raw, probable_causes=causes, guardrails=guardrails)
