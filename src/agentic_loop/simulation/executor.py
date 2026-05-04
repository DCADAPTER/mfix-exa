from __future__ import annotations

from collections.abc import Mapping

from src.agentic_loop.shared.types import CaseProposal
from src.harness.runner import SimulationHarness


class SimulationExecutor:
    """Execute selected cases through the simulation harness."""

    def __init__(self, harness: SimulationHarness):
        """Input: harness object. Output: initialized executor."""
        self.harness = harness

    def run_case(self, case: CaseProposal, iteration: int) -> dict[str, str]:
        """Input: one proposal case + iteration index.

        Output: harness result dict (`status`, `objective`, `stdout`, ...).
        """
        if isinstance(case.patch, Mapping):
            result = self.harness.run_once(case.patch)
        else:
            result = self.harness.run_once(case.patch)
        result["iteration"] = str(iteration)
        return result


# TODO(core):
# - define production-grade implementation tasks for this module.
# - keep this section updated as features are implemented.
