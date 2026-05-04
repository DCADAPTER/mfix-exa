from __future__ import annotations

from src.agentic_loop.shared.types import CaseProposal, Insight


class ActiveLearningFilter:
    """Filter module placeholder: uncertainty/diversity-aware case selection."""

    def select(self, proposals: list[CaseProposal], insight: Insight, budget: int = 3) -> list[CaseProposal]:
        # TODO: uncertainty sampling + diversity + safety constraints.
        ranked = sorted(proposals, key=lambda c: c.expected_gain, reverse=True)
        return ranked[:budget]


# TODO(core):
# - define production-grade implementation tasks for this module.
# - keep this section updated as features are implemented.
