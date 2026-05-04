from __future__ import annotations

from src.agentic_loop.shared.types import CaseProposal
from src.harness.runner import SimulationHarness


class SimulationExecutor:
    def __init__(self, harness: SimulationHarness):
        self.harness = harness

    def run_case(self, case: CaseProposal, iteration: int) -> dict[str, str]:
        return self.harness.run_once(f"iteration={iteration}: {case.patch}")
