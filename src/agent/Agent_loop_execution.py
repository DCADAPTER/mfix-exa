from __future__ import annotations

import typer

from src.agent.services import AgentRuntime
from src.common.config import load_settings

cli = typer.Typer(help="Run iterative agent-harness loop execution.")


@cli.command()
def run(
    config: str = typer.Option(..., "--config", help="Path to settings YAML/JSON"),
    max_iterations: int | None = typer.Option(None, "--max-iterations", help="Override configured max iterations"),
) -> None:
    settings = load_settings(config)
    if max_iterations is not None:
        settings.agent.max_iterations = max_iterations

    runtime = AgentRuntime(settings=settings)
    runtime.loop()


@cli.command("version")
def version() -> None:
    print("mfix-exa agent loop runner")


if __name__ == "__main__":
    cli()
