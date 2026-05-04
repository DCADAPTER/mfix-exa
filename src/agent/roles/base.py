from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AgentContext:
    iteration: int
    goal: str
    plan: str = ""
    input_patch: str = ""
    run_result: dict[str, str] = field(default_factory=dict)
    corrections: str = ""


class AgentRole:
    name: str = "role"

    def act(self, ctx: AgentContext) -> AgentContext:
        raise NotImplementedError
