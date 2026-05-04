from __future__ import annotations

from src.agentic_loop.shared.types import Insight, LoopState


class AnalyzerAgent:
    """Own model/RAG/training asset scope for Analyzer."""

    def __init__(self, model_name: str, rag_index_path: str):
        self.model_name = model_name
        self.rag_index_path = rag_index_path

    def run(self, state: LoopState) -> Insight:
        # TODO: replace with analyzer-specific LLM + RAG retrieval.
        err = state.reference.error_log.lower()
        causes = ["numerical instability"] if "diverge" in err else ["boundary/input mismatch"]
        evidence = [state.reference.error_log[:200]]
        return Insight(causes=causes, evidence=evidence, confidence=0.55)


# TODO(core):
# - define production-grade implementation tasks for this module.
# - keep this section updated as features are implemented.
