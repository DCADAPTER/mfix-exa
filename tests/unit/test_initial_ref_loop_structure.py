from src.agentic_loop.analyzer.agent import AnalyzerAgent
from src.agentic_loop.proposer.agent import ProposerAgent
from src.agentic_loop.shared.types import InitialReference, LoopState


def test_analyzer_proposer_basic() -> None:
    state = LoopState(iteration=0, reference=InitialReference(input_text="x=5", error_log="diverged"))
    insight = AnalyzerAgent("a", "rag/a").run(state)
    cases = ProposerAgent("p", "rag/p").run(insight)
    assert insight.causes
    assert len(cases) == 1
    assert cases[0].patch == {
        "pic.parcels_per_cell_at_pack": "64.0",
        "pic.pressure_coefficient": "50.0",
    }
