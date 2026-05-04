from __future__ import annotations

import re

from src.agent.roles.base import AgentContext, AgentRole


class InputWriterRole(AgentRole):
    name = "input_writer"

    def act(self, ctx: AgentContext) -> AgentContext:
        m = re.search(r"candidate_x=([-+]?\d*\.?\d+)", ctx.plan)
        x = m.group(1) if m else "0"
        ctx.input_patch = f"x={x}"
        return ctx
