import typer
from fastapi import FastAPI
import uvicorn

from src.common.config import load_settings
from src.mcp_server.tools import register_tools

cli = typer.Typer()


@cli.command()
def run(config: str) -> None:
    settings = load_settings(config)
    app = FastAPI(title="MFiX-EXA MCP Server")
    register_tools(app, settings)
    uvicorn.run(app, host=settings.mcp_server.host, port=settings.mcp_server.port)


if __name__ == "__main__":
    cli()
