from __future__ import annotations

from src.agentic_loop.shared.types import CaseProposal, Insight


class ProposerAgent:
    """Generate multiple parameter-change cases from Analyzer insight.

    Input:
      - `insight` (Insight)
      - optional proposal count `n_cases`
    Output:
      - `list[CaseProposal]`
    """

    def __init__(self, model_name: str, rag_index_path: str):
        """Input: model/rag identifiers. Output: initialized ProposerAgent instance."""
        self.model_name = model_name
        self.rag_index_path = rag_index_path

    def run(self, insight: Insight, n_cases: int = 6) -> list[CaseProposal]:
        """Input: analyzer insight.

        Output: candidate cases with patch + expected gain.
        """
        return [
            CaseProposal(
                case_id="case_parcel_weight_lower",
                patch={
                    "pic.parcels_per_cell_at_pack": "64.0",
                    "pic.pressure_coefficient": "50.0",
                },
                expected_gain=0.95,
            )
        ][:n_cases]


# TODO(core):
# - define production-grade implementation tasks for this module.
# - keep this section updated as features are implemented.
