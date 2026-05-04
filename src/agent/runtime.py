import typer

from src.agent.services import AgentRuntime
from src.common.config import load_settings

cli = typer.Typer()


@cli.command()
def run(config: str) -> None:
    settings = load_settings(config)
    runtime = AgentRuntime(settings=settings)
    runtime.loop()


if __name__ == "__main__":
    cli()
