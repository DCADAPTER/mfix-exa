from __future__ import annotations

from src.agentic_loop.shared.types import CaseProposal, Insight


class ActiveLearningFilter:
    """Select executable cases from proposer outputs.

    Input:
      - `proposals`: all candidate cases
      - `insight`: analyzer insight
      - `budget`: max number of cases to keep
    Output:
      - filtered `list[CaseProposal]`
    """

    def select(self, proposals: list[CaseProposal], insight: Insight, budget: int = 3) -> list[CaseProposal]:
        """Input: proposals + insight. Output: top-ranked cases under budget."""
        # TODO: uncertainty sampling + diversity + safety constraints.
        ranked = sorted(proposals, key=lambda c: c.expected_gain, reverse=True)
        return ranked[:budget]


# TODO(core):
# - define production-grade implementation tasks for this module.
# - keep this section updated as features are implemented.
