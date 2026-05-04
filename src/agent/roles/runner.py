from __future__ import annotations

from src.agent.roles.base import AgentContext, AgentRole
from src.harness.runner import SimulationHarness


class RunnerRole(AgentRole):
    name = "runner"

    def __init__(self, harness: SimulationHarness):
        self.harness = harness

    def act(self, ctx: AgentContext) -> AgentContext:
        ctx.run_result = self.harness.run_once(f"iteration={ctx.iteration}: {ctx.input_patch}")
        return ctx
