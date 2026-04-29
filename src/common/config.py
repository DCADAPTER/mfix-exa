from pathlib import Path

import yaml
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


def load_settings(config_path: str | Path) -> Settings:
    with Path(config_path).open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return Settings.model_validate(raw)
