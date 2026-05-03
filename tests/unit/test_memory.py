from src.agent.memory import SlidingWindowMemory


def test_sliding_window_memory_max_turns() -> None:
    mem = SlidingWindowMemory(max_turns=2)
    mem.add("user", "a")
    mem.add("assistant", "b")
    mem.add("user", "c")
    text = mem.to_text()
    assert "a" not in text
    assert "b" in text
    assert "c" in text
