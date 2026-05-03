from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Turn:
    role: str
    content: str


@dataclass
class SlidingWindowMemory:
    max_turns: int = 8
    turns: list[Turn] = field(default_factory=list)

    def add(self, role: str, content: str) -> None:
        self.turns.append(Turn(role=role, content=content))
        if len(self.turns) > self.max_turns:
            self.turns = self.turns[-self.max_turns :]

    def to_text(self) -> str:
        return "\n\n".join(f"[{t.role}]\n{t.content}" for t in self.turns)
