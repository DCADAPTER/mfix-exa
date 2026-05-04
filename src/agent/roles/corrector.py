from __future__ import annotations

from src.agent.roles.base import AgentContext, AgentRole


class CorrectorRole(AgentRole):
    name = "corrector"

    def act(self, ctx: AgentContext) -> AgentContext:
        status = ctx.run_result.get("status", "unknown")
        if status != "ok":
            ctx.corrections = "reduce step / verify bounds / retry"
        else:
            ctx.corrections = "keep direction"
        return ctx
