from src.agent.llm.base import LLMConfig
from src.agent.llm.mock import MockLLMClient
from src.agent.two_stage.analyzer import AnalyzerAgent
from src.agent.two_stage.orchestrator import AnalyzerProposerOrchestrator
from src.agent.two_stage.proposer import ProposerAgent
from src.agent.two_stage.types import IterationState
from src.common.config import load_settings
from src.harness.runner import SimulationHarness


def test_analyzer_proposer_iteration() -> None:
    settings = load_settings("examples/simple_optimization/settings.local.yaml")
    orch = AnalyzerProposerOrchestrator(
        harness=SimulationHarness(settings),
        analyzer=AnalyzerAgent(MockLLMClient(LLMConfig(provider="mock", model="a"))),
        proposer=ProposerAgent(MockLLMClient(LLMConfig(provider="mock", model="p"))),
    )
    state = IterationState(iteration=0, last_input="x=0", last_stdout="", last_status="ok")
    nxt = orch.run_iteration(state)
    assert nxt.iteration == 1
    assert nxt.candidates
    assert nxt.last_input.startswith("x=")
