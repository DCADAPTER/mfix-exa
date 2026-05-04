from __future__ import annotations

import re

from src.agent.llm.base import LLMClient
from src.agent.two_stage.types import AnalyzerInsight, ProposalCase


class ProposerAgent:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def propose(self, insight: AnalyzerInsight, last_input: str, n_cases: int = 4) -> list[ProposalCase]:
        m = re.search(r"x=([-+]?\d*\.?\d+)", last_input)
        x0 = float(m.group(1)) if m else 0.0
        _ = self.llm.generate(f"Propose {n_cases} candidates from insight: {insight.summary}")
        deltas = [-1.0, -0.3, 0.3, 1.0][:n_cases]
        return [
            ProposalCase(case_id=f"case_{i+1}", x=max(-5.0, min(5.0, x0 + d)), rationale=insight.probable_causes[0])
            for i, d in enumerate(deltas)
        ]
