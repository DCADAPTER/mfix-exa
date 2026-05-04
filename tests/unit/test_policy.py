from src.agent.policy import merge_system_instruction


def test_merge_system_instruction() -> None:
    merged = merge_system_instruction("base", "extra")
    assert "base" in merged
    assert "PROJECT_POLICY" in merged
    assert "extra" in merged
