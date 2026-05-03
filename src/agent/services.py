from __future__ import annotations

from dataclasses import dataclass, field

from src.harness.runner import SimulationHarness


@dataclass
class AgentState:
    best_score: float | None = None
    best_plan: str | None = None


@dataclass
class AgentRuntime:
    settings: object
    state: AgentState = field(default_factory=AgentState)

    def _make_plan(self, step: int) -> str:
        return f"iteration={step}: adjust parameters toward stable convergence"

    def _score(self, result: dict[str, str]) -> float:
        # Placeholder deterministic score for skeleton.
        return 1.0 if result.get("status") == "stubbed" else 0.0

    def loop(self) -> None:
        harness = SimulationHarness(self.settings)
        for step in range(self.settings.agent.max_iterations):
            plan = self._make_plan(step)
            result = harness.run_once(plan=plan)
            score = self._score(result)
            if self.state.best_score is None or score >= self.state.best_score:
                self.state.best_score = score
                self.state.best_plan = plan
            print(f"[agent] {plan} -> {result} (score={score:.3f})")

        print(f"[agent] best_plan={self.state.best_plan}, best_score={self.state.best_score}")
