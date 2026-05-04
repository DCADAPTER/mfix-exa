from __future__ import annotations

from src.agentic_loop.shared.types import Insight, LoopState


class AnalyzerAgent:
    """Analyze previous input/error logs and produce structured insight.

    Input:
      - `state` (LoopState): includes initial reference input + error log.
    Output:
      - `Insight`: probable causes, evidence snippets, confidence.
    """

    def __init__(self, model_name: str, rag_index_path: str):
        """Input: model/rag identifiers. Output: initialized AnalyzerAgent instance."""
        self.model_name = model_name
        self.rag_index_path = rag_index_path

    def run(self, state: LoopState) -> Insight:
        """Input: LoopState with `reference.error_log`.

        Output: Insight object used by Proposer/Filter stages.
        """
        # TODO: replace with analyzer-specific LLM + RAG retrieval.
        err = state.reference.error_log.lower()
        causes = ["numerical instability"] if "diverge" in err else ["boundary/input mismatch"]
        evidence = [state.reference.error_log[:200]]
        return Insight(causes=causes, evidence=evidence, confidence=0.55)


# TODO(core):
# - define production-grade implementation tasks for this module.
# - keep this section updated as features are implemented.
