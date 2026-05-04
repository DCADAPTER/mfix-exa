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
        return Insight(
            causes=[
                "Parcel weight is too high. It needs to be lower to approximate the real case."
            ],
            evidence=[state.reference.error_log[:200]],
            confidence=0.55,
        )


# TODO(core):
# - define production-grade implementation tasks for this module.
# - keep this section updated as features are implemented.
