from __future__ import annotations

import typer

from src.agentic_loop.analyzer.agent import AnalyzerAgent
from src.agentic_loop.filtering.active_learning import ActiveLearningFilter
from src.agentic_loop.orchestrator.loop import AgenticSimulationLoop
from src.agentic_loop.proposer.agent import ProposerAgent
from src.agentic_loop.shared.types import InitialReference
from src.agentic_loop.simulation.executor import SimulationExecutor
from src.common.config import load_settings
from src.harness.runner import SimulationHarness

cli = typer.Typer(help="Initial Reference -> Analyzer -> Proposer -> Filter -> Simulation loop")


@cli.command()
def run(
    config: str = typer.Option(..., "--config"),
    initial_input: str = typer.Option(..., "--initial-input"),
    initial_error_log: str = typer.Option(..., "--initial-error-log"),
    analyzer_model: str = typer.Option("analyzer-mini", "--analyzer-model"),
    proposer_model: str = typer.Option("proposer-mini", "--proposer-model"),
) -> None:
    """Input:
      - config path
      - initial input string
      - initial error log string
      - analyzer/proposer model names

    Output:
      - prints Insight + selected cases to stdout.
    """
    settings = load_settings(config)
    harness = SimulationHarness(settings)

    loop = AgenticSimulationLoop(
        analyzer=AnalyzerAgent(model_name=analyzer_model, rag_index_path="rag/analyzer"),
        proposer=ProposerAgent(model_name=proposer_model, rag_index_path="rag/proposer"),
        filter_module=ActiveLearningFilter(),
        simulator=SimulationExecutor(harness),
    )
    state = loop.run_once(0, InitialReference(input_text=initial_input, error_log=initial_error_log))
    print(f"insight={state.insight}")
    print(f"selected_cases={state.selected_cases}")


@cli.command("version")
def version() -> None:
    """Input: none. Output: version-like string to stdout."""
    print("initial-ref loop")


if __name__ == "__main__":
    cli()


# TODO(core):
# - define production-grade implementation tasks for this module.
# - keep this section updated as features are implemented.
