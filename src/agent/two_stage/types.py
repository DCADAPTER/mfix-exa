from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AnalyzerInsight:
    summary: str
    probable_causes: list[str]
    guardrails: list[str]


@dataclass
class ProposalCase:
    case_id: str
    x: float
    rationale: str


@dataclass
class IterationState:
    iteration: int
    last_input: str
    last_stdout: str
    last_status: str
    insight: AnalyzerInsight | None = None
    candidates: list[ProposalCase] = field(default_factory=list)
