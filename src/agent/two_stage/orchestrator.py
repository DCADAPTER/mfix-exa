from __future__ import annotations

from dataclasses import dataclass

from src.agent.two_stage.analyzer import AnalyzerAgent
from src.agent.two_stage.filter import filter_cases
from src.agent.two_stage.proposer import ProposerAgent
from src.agent.two_stage.types import IterationState
from src.harness.runner import SimulationHarness


@dataclass
class AnalyzerProposerOrchestrator:
    harness: SimulationHarness
    analyzer: AnalyzerAgent
    proposer: ProposerAgent

    def run_iteration(self, state: IterationState) -> IterationState:
        insight = self.analyzer.analyze(state)
        cases = self.proposer.propose(insight, state.last_input, n_cases=4)
        filtered = filter_cases(cases)

        best = None
        best_obj = float("inf")
        for c in filtered:
            result = self.harness.run_once(f"iteration={state.iteration}: x={c.x}")
            obj = float(result.get("objective", "inf"))
            if obj < best_obj:
                best = (c, result)
                best_obj = obj

        chosen_input = f"x={best[0].x}" if best else state.last_input
        chosen_result = best[1] if best else {"status": "no_case"}
        return IterationState(
            iteration=state.iteration + 1,
            last_input=chosen_input,
            last_stdout=chosen_result.get("stdout", ""),
            last_status=chosen_result.get("status", "unknown"),
            insight=insight,
            candidates=filtered,
        )
