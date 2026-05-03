from fastapi import FastAPI

from src.common.config import Settings


def register_tools(app: FastAPI, settings: Settings) -> None:
    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "project": settings.project.name}

    @app.post("/tools/parse_output")
    def parse_output(payload: dict) -> dict:
        return {"tool": "parse_output", "received": payload, "todo": "implement parser"}

    @app.post("/tools/validate_input")
    def validate_input(payload: dict) -> dict:
        return {"tool": "validate_input", "received": payload, "todo": "implement validator"}
