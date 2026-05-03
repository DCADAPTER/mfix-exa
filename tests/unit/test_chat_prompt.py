from src.agent.chat import build_prompt


def test_build_prompt_contains_roles() -> None:
    prompt = build_prompt("hello", "sys")
    assert "<|system|>" in prompt
    assert "<|user|>" in prompt
    assert "<|assistant|>" in prompt
