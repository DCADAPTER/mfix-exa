from __future__ import annotations

import typer

from src.agent.roles.orchestrator import MultiAgentOrchestrator
from src.common.config import load_settings
from src.harness.runner import SimulationHarness

cli = typer.Typer(help="Run role-based multi-agent orchestration loop.")


@cli.command()
def run(
    config: str = typer.Option(..., "--config"),
    goal: str = typer.Option("minimize objective", "--goal"),
    max_iterations: int | None = typer.Option(None, "--max-iterations"),
) -> None:
    settings = load_settings(config)
    if max_iterations is not None:
        settings.agent.max_iterations = max_iterations

    harness = SimulationHarness(settings)
    orch = MultiAgentOrchestrator(harness)

    for i in range(settings.agent.max_iterations):
        ctx = orch.run_iteration(i, goal)
        print(
            f"[orchestrator] iter={i} plan={ctx.plan} patch={ctx.input_patch} "
            f"result={ctx.run_result} correction={ctx.corrections}"
        )


@cli.command("version")
def version() -> None:
    print("mfix-exa orchestrated loop runner")


if __name__ == "__main__":
    cli()
