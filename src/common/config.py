from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel


class ProjectConfig(BaseModel):
    name: str
    env: str


class MCPServerConfig(BaseModel):
    host: str
    port: int
    enabled_tools: list[str]


class AgentConfig(BaseModel):
    model_provider: str
    model_name: str
    max_iterations: int


class HarnessConfig(BaseModel):
    simulator_cmd: str
    work_dir: str
    timeout_sec: int


class TrainingConfig(BaseModel):
    base_model: str
    dataset_dir: str
    output_dir: str
    lora_r: int
    lora_alpha: int
    lora_dropout: float


class Settings(BaseModel):
    project: ProjectConfig
    mcp_server: MCPServerConfig
    agent: AgentConfig
    harness: HarnessConfig
    training: TrainingConfig


def _load_text_config(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix == ".json":
        return json.loads(text)

    try:
        import yaml  # type: ignore
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "PyYAML is required for YAML configs. Install with `pip install pyyaml` "
            "or provide a .json config file."
        ) from exc

    return yaml.safe_load(text)


def load_settings(config_path: str | Path) -> Settings:
    path = Path(config_path)
    raw = _load_text_config(path)
    return Settings.model_validate(raw)
