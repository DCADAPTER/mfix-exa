from src.agent.roles.orchestrator import MultiAgentOrchestrator
from src.common.config import load_settings
from src.harness.runner import SimulationHarness


def test_orchestrator_iteration_smoke() -> None:
    settings = load_settings("examples/simple_optimization/settings.local.yaml")
    orch = MultiAgentOrchestrator(SimulationHarness(settings))
    ctx = orch.run_iteration(iteration=0, goal="minimize objective")
    assert ctx.plan
    assert ctx.input_patch.startswith("x=")
    assert "status" in ctx.run_result
