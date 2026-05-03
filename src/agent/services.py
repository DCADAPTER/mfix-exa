from dataclasses import dataclass

from src.common.config import Settings
from src.harness.runner import SimulationHarness


@dataclass
class AgentRuntime:
    settings: Settings

    def loop(self) -> None:
        harness = SimulationHarness(self.settings)
        for step in range(self.settings.agent.max_iterations):
            plan = f"iteration={step}: propose next simulation parameters"
            result = harness.run_once(plan=plan)
            print(f"[agent] {plan} -> {result}")
