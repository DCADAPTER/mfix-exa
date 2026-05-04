from __future__ import annotations

from dataclasses import dataclass

from src.agentic_loop.analyzer.agent import AnalyzerAgent
from src.agentic_loop.filtering.active_learning import ActiveLearningFilter
from src.agentic_loop.proposer.agent import ProposerAgent
from src.agentic_loop.shared.types import InitialReference, LoopState
from src.agentic_loop.simulation.executor import SimulationExecutor


@dataclass
class AgenticSimulationLoop:
    """Orchestrate Analyzer -> Proposer -> Filter -> Simulation."""

    analyzer: AnalyzerAgent
    proposer: ProposerAgent
    filter_module: ActiveLearningFilter
    simulator: SimulationExecutor

    def run_once(self, iteration: int, reference: InitialReference) -> LoopState:
        """Input:
          - `iteration`: loop index
          - `reference`: initial input + error log context

        Output:
          - updated `LoopState` containing insight/proposals/selected cases.
        """
        state = LoopState(iteration=iteration, reference=reference)

        state.insight = self.analyzer.run(state)
        state.proposals = self.proposer.run(state.insight)
        state.selected_cases = self.filter_module.select(state.proposals, state.insight, budget=3)

        for case in state.selected_cases:
            state.simulation_results.append(self.simulator.run_case(case, iteration))
        return state


# TODO(core):
# - define production-grade implementation tasks for this module.
# - keep this section updated as features are implemented.
