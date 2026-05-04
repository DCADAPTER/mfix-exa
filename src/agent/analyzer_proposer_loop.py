from __future__ import annotations

import typer

from src.agent.llm.base import LLMConfig
from src.agent.llm.mock import MockLLMClient
from src.agent.two_stage.analyzer import AnalyzerAgent
from src.agent.two_stage.orchestrator import AnalyzerProposerOrchestrator
from src.agent.two_stage.proposer import ProposerAgent
from src.agent.two_stage.types import IterationState
from src.common.config import load_settings
from src.harness.runner import SimulationHarness

cli = typer.Typer(help="Analyzer+Proposer orchestration loop.")


@cli.command()
def run(
    config: str = typer.Option(..., "--config"),
    analyzer_model: str = typer.Option("analyzer-mini", "--analyzer-model"),
    proposer_model: str = typer.Option("proposer-mini", "--proposer-model"),
    max_iterations: int | None = typer.Option(None, "--max-iterations"),
) -> None:
    settings = load_settings(config)
    if max_iterations is not None:
        settings.agent.max_iterations = max_iterations

    harness = SimulationHarness(settings)
    analyzer = AnalyzerAgent(MockLLMClient(LLMConfig(provider="mock", model=analyzer_model)))
    proposer = ProposerAgent(MockLLMClient(LLMConfig(provider="mock", model=proposer_model)))
    orch = AnalyzerProposerOrchestrator(harness, analyzer, proposer)

    state = IterationState(iteration=0, last_input="x=0", last_stdout="", last_status="ok")
    for _ in range(settings.agent.max_iterations):
        state = orch.run_iteration(state)
        print(
            f"[A/P loop] iter={state.iteration} status={state.last_status} "
            f"input={state.last_input} candidates={len(state.candidates)}"
        )


@cli.command("version")
def version() -> None:
    print("mfix-exa analyzer-proposer loop")


if __name__ == "__main__":
    cli()
