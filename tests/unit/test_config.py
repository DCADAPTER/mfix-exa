from src.common.config import load_settings


def test_load_settings() -> None:
    settings = load_settings("configs/settings.example.yaml")
    assert settings.project.name == "mfix-exa-agentic"
    assert settings.agent.max_iterations > 0
