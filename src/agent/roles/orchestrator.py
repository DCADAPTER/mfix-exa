from __future__ import annotations

from dataclasses import dataclass

from src.agent.roles.base import AgentContext
from src.agent.roles.corrector import CorrectorRole
from src.agent.roles.input_writer import InputWriterRole
from src.agent.roles.prechecker import PrecheckerRole
from src.agent.roles.runner import RunnerRole
from src.harness.runner import SimulationHarness


@dataclass
class MultiAgentOrchestrator:
    harness: SimulationHarness

    def run_iteration(self, iteration: int, goal: str) -> AgentContext:
        ctx = AgentContext(iteration=iteration, goal=goal)
        for role in (PrecheckerRole(), InputWriterRole(), RunnerRole(self.harness), CorrectorRole()):
            ctx = role.act(ctx)
        return ctx
