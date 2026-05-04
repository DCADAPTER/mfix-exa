from __future__ import annotations

from collections.abc import Mapping
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
    patch: str | Mapping[str, object]
    expected_gain: float


@dataclass
class LoopState:
    iteration: int
    reference: InitialReference
    insight: Insight | None = None
    proposals: list[CaseProposal] = field(default_factory=list)
    selected_cases: list[CaseProposal] = field(default_factory=list)
    simulation_results: list[dict[str, str]] = field(default_factory=list)
