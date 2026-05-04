from __future__ import annotations

from src.agent.two_stage.types import ProposalCase


def filter_cases(cases: list[ProposalCase], x_min: float = -5.0, x_max: float = 5.0) -> list[ProposalCase]:
    return [c for c in cases if x_min <= c.x <= x_max]
