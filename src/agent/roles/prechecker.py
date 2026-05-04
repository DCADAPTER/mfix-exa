from __future__ import annotations

from src.agent.roles.base import AgentContext, AgentRole


class PrecheckerRole(AgentRole):
    name = "prechecker"

    def act(self, ctx: AgentContext) -> AgentContext:
        if not ctx.goal:
            raise ValueError("goal is required")
        ctx.plan = f"iter={ctx.iteration}; goal={ctx.goal}; candidate_x={max(-5, min(5, 5-ctx.iteration))}"
        return ctx
