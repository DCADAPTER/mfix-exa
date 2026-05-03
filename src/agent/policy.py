from __future__ import annotations

from pathlib import Path


def load_instruction_file(path: str | None) -> str:
    if not path:
        return ""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"instruction file not found: {path}")
    return p.read_text(encoding="utf-8").strip()


def merge_system_instruction(base: str, extra: str) -> str:
    if not extra:
        return base
    if not base:
        return extra
    return f"{base}\n\n[PROJECT_POLICY]\n{extra}"
