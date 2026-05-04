from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class InitialReference:
    input_text: str
    error_log: str


@dataclass
class Insight:
    causes: list[str]
    evidence: list[str]
    confidence: float


@dataclass
class CaseProposal:
    case_id: str
    patch: str
    expected_gain: float


@dataclass
class LoopState:
    iteration: int
    reference: InitialReference
    insight: Insight | None = None
    proposals: list[CaseProposal] = field(default_factory=list)
    selected_cases: list[CaseProposal] = field(default_factory=list)
