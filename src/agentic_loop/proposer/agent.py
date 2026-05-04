from __future__ import annotations

from src.agentic_loop.shared.types import CaseProposal, Insight


class ProposerAgent:
    """Own model/RAG/training asset scope for Proposer."""

    def __init__(self, model_name: str, rag_index_path: str):
        self.model_name = model_name
        self.rag_index_path = rag_index_path

    def run(self, insight: Insight, n_cases: int = 6) -> list[CaseProposal]:
        base = [
            ("case_1", "x=1.5", 0.20),
            ("case_2", "x=2.0", 0.35),
            ("case_3", "x=2.5", 0.55),
            ("case_4", "x=3.0", 0.95),
            ("case_5", "x=3.5", 0.60),
            ("case_6", "x=4.0", 0.30),
        ]
        return [CaseProposal(*row) for row in base[:n_cases]]


# TODO(core):
# - define production-grade implementation tasks for this module.
# - keep this section updated as features are implemented.
